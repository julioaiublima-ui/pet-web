from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, RunContext, function_tool, room_io
from livekit.agents.llm import ToolError
from livekit.plugins import openai


RAIZ_PROJETO = Path(__file__).resolve().parent

load_dotenv(RAIZ_PROJETO / ".env")
load_dotenv(RAIZ_PROJETO / ".env.local", override=True)

logging.basicConfig(
    level=os.getenv("JARVIS_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("jarvis-assistant")


PROMPT_SISTEMA = """
Voce e um assistente operacional de voz inspirado em sistemas de bordo de cinema.
Seu papel e servir como servidor central local do Mac do Operador.

Personalidade:
- Perspicaz, altamente inteligente, formal sem ser lento.
- Chame o usuario de "Senhor" ou "Operador" com naturalidade, sem repetir em toda frase.
- Responda em portugues brasileiro, com frases curtas e prontas para voz.
- Seja preciso, sereno e direto. Evite listas longas quando estiver falando.
- Avise rapidamente quando for iniciar uma tarefa demorada no navegador.

Uso de ferramentas:
- Use a ferramenta controlar_chrome quando o usuario pedir pesquisa, leitura, compra,
  preenchimento de sites, comparacao de informacoes online, uso de email no navegador,
  ou qualquer tarefa que dependa de uma pagina web.
- Depois da ferramenta terminar, resuma o resultado em linguagem natural.
- Se a ferramenta falhar, explique a falha sem derrubar a conversa e proponha o proximo passo.

Seguranca operacional:
- Nao finalize compras, pagamentos, envio de emails, exclusao de dados, mudancas de senha,
  alteracoes de conta ou qualquer acao irreversivel sem confirmacao explicita do Operador.
- Para credenciais, codigos 2FA, CAPTCHAs e permissoes do macOS, peca que o Operador assuma.
- Nao tente burlar controles de seguranca de sites.
""".strip()


def _bool_env(nome: str, padrao: bool) -> bool:
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "sim", "on"}


def _int_env(nome: str, padrao: int) -> int:
    valor = os.getenv(nome)
    if not valor:
        return padrao
    try:
        return int(valor)
    except ValueError:
        logger.warning("Valor invalido para %s=%r; usando %s.", nome, valor, padrao)
        return padrao


def _limitar_texto(texto: str, limite: int = 2200) -> str:
    texto = " ".join(str(texto or "").split())
    if len(texto) <= limite:
        return texto
    return f"{texto[: limite - 3]}..."


@dataclass(frozen=True)
class ConfiguracaoAssistente:
    nome_agente: str
    modelo_realtime: str
    voz_realtime: str
    vad_eagerness: str
    reducao_ruido: str | None
    modelo_navegador: str
    navegador_headless: bool
    navegador_max_steps: int
    navegador_timeout_s: int
    usar_chrome_sistema: bool
    perfil_chrome: str | None
    caminho_chrome: str
    diretorio_perfil_isolado: Path
    diretorio_downloads: Path
    diretorio_traces: Path
    gravar_video: bool

    @classmethod
    def do_ambiente(cls) -> "ConfiguracaoAssistente":
        perfil = os.getenv("JARVIS_CHROME_PROFILE", "").strip() or None
        ruido = os.getenv("JARVIS_NOISE_REDUCTION", "near_field").strip() or None

        return cls(
            nome_agente=os.getenv("JARVIS_AGENT_NAME", "jarvis-central"),
            modelo_realtime=os.getenv("JARVIS_REALTIME_MODEL", "gpt-4o-realtime-preview"),
            voz_realtime=os.getenv("JARVIS_REALTIME_VOICE", "coral"),
            vad_eagerness=os.getenv("JARVIS_VAD_EAGERNESS", "medium"),
            reducao_ruido=ruido,
            modelo_navegador=os.getenv("JARVIS_BROWSER_MODEL", "gpt-4.1-mini"),
            navegador_headless=_bool_env("JARVIS_BROWSER_HEADLESS", False),
            navegador_max_steps=_int_env("JARVIS_BROWSER_MAX_STEPS", 40),
            navegador_timeout_s=_int_env("JARVIS_BROWSER_TIMEOUT_SECONDS", 240),
            usar_chrome_sistema=_bool_env("JARVIS_USE_SYSTEM_CHROME", True),
            perfil_chrome=perfil,
            caminho_chrome=os.getenv(
                "JARVIS_CHROME_PATH",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ),
            diretorio_perfil_isolado=RAIZ_PROJETO / ".jarvis_chrome_profile",
            diretorio_downloads=RAIZ_PROJETO / "downloads" / "browser-use",
            diretorio_traces=RAIZ_PROJETO / "traces" / "browser-use",
            gravar_video=_bool_env("JARVIS_BROWSER_RECORD_VIDEO", False),
        )


CONFIG = ConfiguracaoAssistente.do_ambiente()


def criar_turn_detection() -> Any:
    configuracao = {
        "type": "semantic_vad",
        "eagerness": CONFIG.vad_eagerness,
        "create_response": True,
        "interrupt_response": True,
    }

    try:
        from openai.types.beta.realtime.session import TurnDetection

        return TurnDetection(**configuracao)
    except Exception:
        try:
            from openai.types import realtime

            return realtime.realtime_audio_input_turn_detection.SemanticVad(**configuracao)
        except Exception:
            return configuracao


def criar_modelo_realtime() -> Any:
    parametros: dict[str, Any] = {
        "model": CONFIG.modelo_realtime,
        "voice": CONFIG.voz_realtime,
        "modalities": ["text", "audio"],
        "turn_detection": criar_turn_detection(),
    }

    if CONFIG.reducao_ruido:
        parametros["input_audio_noise_reduction"] = CONFIG.reducao_ruido

    try:
        return openai.realtime.RealtimeModel(**parametros)
    except TypeError:
        parametros.pop("input_audio_noise_reduction", None)
        return openai.realtime.RealtimeModel(**parametros)


class AutomacaoChrome:
    def __init__(self, config: ConfiguracaoAssistente) -> None:
        self.config = config
        self._lock = asyncio.Lock()

    async def executar(self, tarefa: str) -> str:
        tarefa = tarefa.strip()
        if len(tarefa) < 4:
            raise ToolError("A tarefa do navegador ficou curta demais para executar com seguranca.")

        async with self._lock:
            try:
                return await asyncio.wait_for(
                    self._executar_com_browser_use(tarefa),
                    timeout=self.config.navegador_timeout_s,
                )
            except asyncio.TimeoutError as exc:
                raise ToolError(
                    "A automacao do Chrome excedeu o tempo limite. Posso tentar de novo com passos menores."
                ) from exc
            except ToolError:
                raise
            except Exception as exc:
                logger.exception("Falha na automacao do Chrome.")
                raise ToolError(
                    "A automacao do Chrome falhou antes de concluir. Verifique se o Chrome e o Playwright estao instalados."
                ) from exc

    async def _executar_com_browser_use(self, tarefa: str) -> str:
        BrowserUseAgent, Browser, ChatOpenAI = self._carregar_browser_use()

        self.config.diretorio_downloads.mkdir(parents=True, exist_ok=True)
        self.config.diretorio_traces.mkdir(parents=True, exist_ok=True)
        self.config.diretorio_perfil_isolado.mkdir(parents=True, exist_ok=True)

        llm = ChatOpenAI(model=self.config.modelo_navegador, temperature=0.0)
        browser = await self._iniciar_browser(Browser)

        try:
            tarefa_controlada = self._montar_tarefa_controlada(tarefa)
            agente = BrowserUseAgent(
                task=tarefa_controlada,
                llm=llm,
                browser=browser,
                use_vision=True,
                vision_detail_level="auto",
                max_failures=3,
                final_response_after_failure=True,
                save_conversation_path=str(self.config.diretorio_traces / "conversa_browser_use.json"),
            )

            historico = await agente.run(max_steps=self.config.navegador_max_steps)
            return self._formatar_resultado(historico)
        finally:
            await self._fechar_browser(browser)

    def _carregar_browser_use(self) -> tuple[Any, Any, Any]:
        try:
            from browser_use import Agent as BrowserUseAgent
            from browser_use import Browser

            try:
                from browser_use import ChatOpenAI
            except ImportError:
                from langchain_openai import ChatOpenAI

            return BrowserUseAgent, Browser, ChatOpenAI
        except ImportError as exc:
            raise ToolError(
                "Dependencias de automacao ausentes. Instale com pip install -r requirements-jarvis.txt."
            ) from exc

    async def _iniciar_browser(self, Browser: Any) -> Any:
        if self.config.usar_chrome_sistema:
            try:
                browser = Browser.from_system_chrome(
                    profile_directory=self.config.perfil_chrome,
                    headless=self.config.navegador_headless,
                    keep_alive=False,
                    window_size={"width": 1440, "height": 950},
                    downloads_path=str(self.config.diretorio_downloads),
                    traces_dir=str(self.config.diretorio_traces),
                    record_video_dir=str(self.config.diretorio_traces / "video")
                    if self.config.gravar_video
                    else None,
                )
                await browser.start()
                return browser
            except Exception as exc:
                logger.warning(
                    "Nao consegui iniciar o Chrome do sistema; tentando perfil isolado. Erro: %s",
                    exc,
                )

        browser = Browser(
            executable_path=self.config.caminho_chrome,
            headless=self.config.navegador_headless,
            user_data_dir=str(self.config.diretorio_perfil_isolado),
            keep_alive=False,
            window_size={"width": 1440, "height": 950},
            downloads_path=str(self.config.diretorio_downloads),
            traces_dir=str(self.config.diretorio_traces),
            record_video_dir=str(self.config.diretorio_traces / "video")
            if self.config.gravar_video
            else None,
        )
        await browser.start()
        return browser

    async def _fechar_browser(self, browser: Any) -> None:
        metodo = getattr(browser, "close", None) or getattr(browser, "stop", None)
        if not metodo:
            return
        try:
            await metodo()
        except Exception:
            logger.exception("Falha ao fechar a sessao do navegador.")

    def _montar_tarefa_controlada(self, tarefa: str) -> str:
        return f"""
Execute a tarefa abaixo no Google Chrome usando navegacao visual e screenshots quando necessario.
Retorne somente um resumo final em portugues brasileiro, curto e adequado para ser falado em voz alta.

Limites obrigatorios:
- Nao finalize compras, pagamentos, envios, exclusoes ou mudancas irreversiveis.
- Se a tarefa exigir login, 2FA, CAPTCHA ou permissao sensivel, pare e diga exatamente o que o Operador precisa fazer.
- Para compras, voce pode pesquisar, comparar, abrir produto e preparar carrinho, mas deve parar antes do pagamento.
- Para email, voce pode pesquisar e resumir mensagens visiveis, mas nao envie, apague ou arquive nada sem confirmacao explicita.
- Cite os sites principais visitados no resumo.

Tarefa do Operador:
{tarefa}
""".strip()

    def _formatar_resultado(self, historico: Any) -> str:
        final = self._chamar_ou_vazio(historico, "final_result")
        urls = self._chamar_ou_vazio(historico, "urls", padrao=[])
        erros = [erro for erro in (self._chamar_ou_vazio(historico, "errors", padrao=[]) or []) if erro]
        screenshots = self._chamar_ou_vazio(historico, "screenshot_paths", padrao=[])
        concluido = self._chamar_ou_vazio(historico, "is_done")
        sucesso = self._chamar_ou_vazio(historico, "is_successful")

        partes = [
            "Resumo da automacao do Chrome:",
            _limitar_texto(str(final or "A tarefa terminou sem resultado textual final.")),
        ]

        if urls:
            partes.append("Sites visitados: " + ", ".join(map(str, urls[-5:])))

        if screenshots:
            partes.append("Prints salvos em: " + ", ".join(map(str, screenshots[-3:])))

        if erros:
            partes.append("Ocorreram avisos internos: " + _limitar_texto(str(erros[-1]), 500))

        if concluido is not None:
            partes.append(f"Concluido: {concluido}. Sucesso: {sucesso}.")

        return "\n".join(partes)

    def _chamar_ou_vazio(self, objeto: Any, nome: str, padrao: Any = None) -> Any:
        atributo = getattr(objeto, nome, None)
        if atributo is None:
            return padrao
        try:
            return atributo() if callable(atributo) else atributo
        except Exception:
            logger.debug("Nao foi possivel ler historico.%s", nome, exc_info=True)
            return padrao


class AssistenteCentral(Agent):
    def __init__(self, config: ConfiguracaoAssistente) -> None:
        self.automacao_chrome = AutomacaoChrome(config)
        super().__init__(instructions=PROMPT_SISTEMA)

    @function_tool(
        name="controlar_chrome",
        description=(
            "Executa uma tarefa no Google Chrome usando browser-use. "
            "Use para pesquisar, comparar informacoes, ler paginas, preencher formularios "
            "ou preparar acoes no navegador. Nao finaliza compras, pagamentos, envios "
            "ou alteracoes irreversiveis sem confirmacao explicita."
        ),
    )
    async def controlar_chrome(self, context: RunContext, tarefa: str) -> str | None:
        """Controle autonomo do Google Chrome.

        Args:
            tarefa: Instrucao natural do Operador para executar no navegador.
        """
        context.session.say(
            "Entendido, Senhor. Vou operar o Chrome e retorno com um resumo.",
            add_to_chat_ctx=False,
        )

        tarefa_browser = asyncio.create_task(self.automacao_chrome.executar(tarefa))
        await context.speech_handle.wait_if_not_interrupted([tarefa_browser])

        if context.speech_handle.interrupted:
            tarefa_browser.cancel()
            try:
                await tarefa_browser
            except asyncio.CancelledError:
                pass
            return None

        return tarefa_browser.result()


server = AgentServer()


@server.rtc_session(agent_name=CONFIG.nome_agente)
async def sessao_jarvis(ctx: agents.JobContext) -> None:
    session = AgentSession(llm=criar_modelo_realtime())

    await session.start(
        room=ctx.room,
        agent=AssistenteCentral(CONFIG),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(),
        ),
    )

    await session.generate_reply(
        instructions=(
            "Cumprimente o Operador em portugues, de forma breve, e diga que o nucleo de voz "
            "e a automacao do Chrome estao online."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
