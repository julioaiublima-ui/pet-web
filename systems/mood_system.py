import json
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_AUTOMACOES = PASTA_PROJETO / "automacoes.json"
AVISOS_POR_APP = {
    "Code": {
        "segundos": 45 * 60,
        "mensagem": "Você está no VS Code faz um tempinho. Se tiver erro, cola aqui que eu tento ajudar.",
    },
    "Chrome": {
        "segundos": 35 * 60,
        "mensagem": "Muita pesquisa aberta por aqui... quer organizar o foco? 👀",
    },
    "Discord": {
        "segundos": 25 * 60,
        "mensagem": "Discord por bastante tempo. Será que virou pausa infinita? 😄",
    },
    "YouTube": {
        "segundos": 20 * 60,
        "mensagem": "YouTube está prendendo sua atenção. Ainda faz parte do plano? 👀",
    },
}
INTERVALO_REPETIR_AVISO = 30 * 60
COMANDOS_CONFIRMACAO = ("sim", "s", "pode", "confirmar", "confirma", "ok", "executar", "executa")
COMANDOS_CANCELAMENTO = ("nao", "n", "cancelar", "cancela", "melhor nao")
APLICATIVOS_CONHECIDOS = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "safari": "Safari",
    "code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "discord": "Discord",
    "spotify": "Spotify",
    "terminal": "Terminal",
    "finder": "Finder",
}
ATALHOS_NAVEGACAO = {
    "nova_aba": ("nova aba", "abrir nova aba"),
    "fechar_aba": ("fechar aba", "fechar guia"),
    "recarregar": ("recarregar pagina", "atualizar pagina", "recarregar"),
    "proxima_aba": ("proxima aba", "proxima guia", "ir para proxima aba"),
    "aba_anterior": ("aba anterior", "guia anterior", "ir para aba anterior"),
}
TECLAS_COMANDO = {
    "enter": "enter",
    "tab": "tab",
    "esc": "esc",
    "escape": "esc",
    "espaco": "space",
    "space": "space",
    "backspace": "backspace",
    "delete": "delete",
}


class AutomacoesMarcy:
    def __init__(self, arquivo=ARQUIVO_AUTOMACOES):
        caminho = Path(arquivo)
        if not caminho.is_absolute():
            caminho = PASTA_PROJETO / caminho

        self.caminho = caminho
        self.dados = self.carregar_dados()

    def carregar_dados(self):
        padrao = {
            "ativo": True,
            "lembretes": [],
            "pomodoro": {
                "ativo": False,
                "fase": "",
                "fim": "",
                "foco_minutos": 25,
                "pausa_minutos": 5,
            },
            "app_atual": "",
            "inicio_app": "",
            "ultimo_aviso_app": "",
            "acao_pendente": None,
        }

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            dados = {}

        return self.mesclar_dados(padrao, dados)

    def mesclar_dados(self, padrao, dados):
        resultado = padrao.copy()

        for chave, valor in dados.items():
            if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
                resultado[chave] = self.mesclar_dados(resultado[chave], valor)
            else:
                resultado[chave] = valor

        return resultado

    def salvar_dados(self):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump(self.dados, arquivo, ensure_ascii=False, indent=2)

    def executar_comando(self, texto, app=""):
        texto_original = texto.strip()
        texto_normalizado = self.normalizar_texto(texto_original)

        if not texto_original:
            return self.resposta(False, "")

        pendente = self.responder_acao_pendente(texto_normalizado)
        if pendente:
            return pendente

        if texto_normalizado in ("ajuda", "comandos", "help"):
            return self.resposta(True, self.texto_ajuda())

        if texto_normalizado in ("status", "estado"):
            return self.resposta(True, self.texto_status(app))

        if "pausar automa" in texto_normalizado:
            self.dados["ativo"] = False
            self.salvar_dados()
            return self.resposta(True, "Prontinho, pausei as automações automáticas.")

        if "ativar automa" in texto_normalizado or "ligar automa" in texto_normalizado:
            self.dados["ativo"] = True
            self.salvar_dados()
            return self.resposta(True, "Automações ligadas de novo! Vou ficar atenta.")

        if texto_normalizado in ("cancelar pomodoro", "parar pomodoro", "cancelar foco"):
            self.dados["pomodoro"]["ativo"] = False
            self.salvar_dados()
            return self.resposta(True, "Pomodoro cancelado. Respira um pouco também, tá?")

        lembrete = self.tentar_criar_lembrete(texto_original)
        if lembrete:
            return lembrete

        pomodoro = self.tentar_iniciar_pomodoro(texto_normalizado)
        if pomodoro:
            return pomodoro

        automacao_ui = self.tentar_preparar_automacao_ui(texto_original, texto_normalizado)
        if automacao_ui:
            return automacao_ui

        abertura = self.tentar_preparar_abertura(texto_original, texto_normalizado)
        if abertura:
            return abertura

        if texto_normalizado in ("sair", "fechar", "tchau"):
            return self.resposta(True, "Tá bom, vou descansar um pouquinho.", {"tipo": "fechar"})

        return self.resposta(False, "")

    def responder_acao_pendente(self, texto):
        acao = self.dados.get("acao_pendente")
        if not acao:
            return None

        if texto in COMANDOS_CONFIRMACAO:
            self.dados["acao_pendente"] = None
            self.salvar_dados()

            mensagem = acao.get("mensagem_confirmada") or f"Ok, vou {self.descrever_acao(acao)}."
            return self.resposta(True, mensagem, acao)

        if texto in COMANDOS_CANCELAMENTO:
            self.dados["acao_pendente"] = None
            self.salvar_dados()
            return self.resposta(True, "Beleza, não vou fazer isso.")

        return None

    def tentar_criar_lembrete(self, texto):
        padroes = [
            r"(?:me\s+)?lembra(?:r|re)?(?:\s+de)?\s+(.+?)\s+em\s+(\d+)\s*(segundos?|s|minutos?|mins?|m|horas?|h)\b",
            r"lembrete\s+(.+?)\s+em\s+(\d+)\s*(segundos?|s|minutos?|mins?|m|horas?|h)\b",
            r"(?:me\s+)?lembra(?:r|re)?\s+em\s+(\d+)\s*(segundos?|s|minutos?|mins?|m|horas?|h)\s+(?:de\s+)?(.+)",
        ]

        for padrao in padroes:
            resultado = re.search(padrao, texto, re.IGNORECASE)
            if not resultado:
                continue

            grupos = resultado.groups()
            if grupos[0].isdigit():
                quantidade = int(grupos[0])
                unidade = grupos[1]
                mensagem = grupos[2].strip()
            else:
                mensagem = grupos[0].strip()
                quantidade = int(grupos[1])
                unidade = grupos[2]

            return self.criar_lembrete(mensagem, quantidade, unidade)

        return None

    def criar_lembrete(self, mensagem, quantidade, unidade):
        agora = datetime.now()
        unidade = unidade.lower()

        if unidade.startswith("s"):
            quando = agora + timedelta(seconds=quantidade)
        elif unidade.startswith("h"):
            quando = agora + timedelta(hours=quantidade)
        else:
            quando = agora + timedelta(minutes=quantidade)

        self.dados["lembretes"].append({
            "texto": mensagem,
            "criado": agora.isoformat(timespec="seconds"),
            "quando": quando.isoformat(timespec="seconds"),
            "entregue": False,
        })
        self.salvar_dados()

        tempo = self.texto_tempo(quantidade, unidade)
        return self.resposta(True, f"Combinado! Vou lembrar de {mensagem} em {tempo}.")

    def tentar_iniciar_pomodoro(self, texto):
        if "pomodoro" not in texto and "foco" not in texto:
            return None

        resultado = re.search(r"(\d+)", texto)
        minutos = int(resultado.group(1)) if resultado else 25
        minutos = max(1, min(minutos, 120))

        self.dados["pomodoro"] = {
            "ativo": True,
            "fase": "foco",
            "fim": (datetime.now() + timedelta(minutes=minutos)).isoformat(timespec="seconds"),
            "foco_minutos": minutos,
            "pausa_minutos": 5,
        }
        self.salvar_dados()

        return self.resposta(True, f"Pomodoro de {self.texto_tempo(minutos, 'minutos')} iniciado. Modo foco!")

    def tentar_preparar_automacao_ui(self, texto_original, texto_normalizado):
        for tentativa in (
            self.tentar_preparar_atalho,
            self.tentar_preparar_tecla,
            self.tentar_preparar_clique,
            self.tentar_preparar_digitacao,
        ):
            resultado = tentativa(texto_original, texto_normalizado)
            if resultado:
                return resultado

        return None

    def tentar_preparar_atalho(self, _texto_original, texto_normalizado):
        for nome_atalho, frases in ATALHOS_NAVEGACAO.items():
            if texto_normalizado in frases:
                acao = {"tipo": "atalho", "atalho": nome_atalho}
                return self.preparar_acao(
                    acao,
                    f"Quer que eu execute: {self.descrever_acao(acao)}? Responda sim ou não.",
                    f"Ok, vou executar: {self.descrever_acao(acao)}.",
                )

        return None

    def tentar_preparar_tecla(self, _texto_original, texto_normalizado):
        resultado = re.search(r"\bpressionar\s+([a-z]+)\b", texto_normalizado)
        if not resultado:
            return None

        tecla = TECLAS_COMANDO.get(resultado.group(1))
        if not tecla:
            return self.resposta(True, "Essa tecla ainda não está liberada para automação.")

        acao = {"tipo": "pressionar", "tecla": tecla}
        return self.preparar_acao(
            acao,
            f"Quer que eu pressione {tecla}? Responda sim ou não.",
            f"Ok, vou pressionar {tecla}.",
        )

    def tentar_preparar_clique(self, _texto_original, texto_normalizado):
        resultado = re.search(
            r"\b(?:clicar|clique)\s+(?:em\s+)?(-?\d{1,5})\s*(?:,|\s)\s*(-?\d{1,5})\b",
            texto_normalizado,
        )

        if resultado:
            x = int(resultado.group(1))
            y = int(resultado.group(2))

            if x < 0 or y < 0:
                return self.resposta(True, "Consigo clicar só em coordenadas positivas da tela.")

            acao = {"tipo": "clicar", "x": x, "y": y}
            return self.preparar_acao(
                acao,
                f"Quer que eu clique em ({x}, {y})? Responda sim ou não.",
                f"Ok, vou clicar em ({x}, {y}).",
            )

        if re.search(r"\b(?:clicar|clique)\b", texto_normalizado):
            return self.resposta(
                True,
                "Ainda não reconheço botões pelo nome. Posso clicar por coordenadas, tipo: clicar em 450, 300.",
            )

        return None

    def tentar_preparar_digitacao(self, texto_original, _texto_normalizado):
        resultado = re.search(
            r"\b(?:digitar|escrever na tela|preencher campo com)\s+(.+)",
            texto_original,
            re.IGNORECASE,
        )
        if not resultado:
            return None

        texto = resultado.group(1).strip().strip("\"'")
        if not texto:
            return self.resposta(True, "Me diga qual texto você quer que eu digite.")

        if len(texto) > 500:
            return self.resposta(True, "Esse texto está grande demais para eu digitar com segurança.")

        acao = {"tipo": "digitar", "texto": texto}
        return self.preparar_acao(
            acao,
            f"Quer que eu digite: {texto}? Responda sim ou não.",
            "Ok, vou digitar o texto confirmado.",
        )

    def tentar_preparar_abertura(self, texto, texto_normalizado):
        resultado = re.search(r"\babrir\s+(.+)", texto, re.IGNORECASE)
        if not resultado:
            return None

        destino_original = resultado.group(1).strip()
        destino = texto_normalizado.split("abrir", 1)[1].strip()
        tipo_forcado = ""

        for prefixo, tipo in (
            ("app ", "app"),
            ("aplicativo ", "app"),
            ("site ", "site"),
            ("pagina ", "site"),
        ):
            if destino.startswith(prefixo):
                destino = destino[len(prefixo):].strip()
                destino_original = destino_original[len(prefixo):].strip()
                tipo_forcado = tipo
                break

        atalhos = {
            "github": "https://github.com",
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "ollama": "https://ollama.com",
        }

        if tipo_forcado != "app" and destino in atalhos:
            return self.preparar_abertura_url(atalhos[destino])

        if tipo_forcado != "site" and destino in APLICATIVOS_CONHECIDOS:
            app_nome = APLICATIVOS_CONHECIDOS[destino]
            acao = {"tipo": "abrir_app", "app": app_nome}
            return self.preparar_acao(
                acao,
                f"Quer que eu abra o app {app_nome}? Responda sim ou não.",
                f"Ok, vou abrir {app_nome}.",
            )

        url = destino_original
        if "." not in url and not url.startswith(("http://", "https://")):
            return self.resposta(
                True,
                "Consigo abrir sites ou apps conhecidos. Exemplos: abrir github.com; abrir chrome.",
            )

        if " " in url:
            return self.resposta(True, "Esse endereço parece ter espaços. Me manda só a URL certinha.")

        return self.preparar_abertura_url(url)

    def preparar_abertura_url(self, url):
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        acao = {"tipo": "abrir_url", "url": url}
        return self.preparar_acao(
            acao,
            f"Quer que eu abra {url}? Responda sim ou não.",
            f"Abrindo {url}",
        )

    def preparar_acao(self, acao, pergunta, mensagem_confirmada):
        acao = dict(acao)
        acao["descricao"] = self.descrever_acao(acao)
        acao["mensagem_confirmada"] = mensagem_confirmada
        self.dados["acao_pendente"] = acao
        self.salvar_dados()

        return self.resposta(True, pergunta)

    def descrever_acao(self, acao):
        tipo = acao.get("tipo")

        if tipo == "abrir_url":
            return f"abrir {acao.get('url', '')}"
        if tipo == "abrir_app":
            return f"abrir {acao.get('app', '')}"
        if tipo == "clicar":
            return f"clicar em ({acao.get('x')}, {acao.get('y')})"
        if tipo == "digitar":
            return "digitar texto"
        if tipo == "pressionar":
            return f"pressionar {acao.get('tecla', '')}"
        if tipo == "atalho":
            nomes = {
                "nova_aba": "abrir nova aba",
                "fechar_aba": "fechar aba",
                "recarregar": "recarregar página",
                "proxima_aba": "ir para a próxima aba",
                "aba_anterior": "ir para a aba anterior",
            }
            return nomes.get(acao.get("atalho"), "executar atalho")

        return "executar ação"

    def verificar_eventos(self, app=""):
        mensagens = []
        mensagens.extend(self.verificar_lembretes())

        if self.dados.get("ativo", True):
            mensagem_pomodoro = self.verificar_pomodoro()
            if mensagem_pomodoro:
                mensagens.append(mensagem_pomodoro)

            mensagem_app = self.verificar_app(app)
            if mensagem_app:
                mensagens.append(mensagem_app)

        if mensagens:
            self.salvar_dados()

        return mensagens

    def verificar_lembretes(self):
        agora = datetime.now()
        mensagens = []

        for lembrete in self.dados.get("lembretes", []):
            if lembrete.get("entregue"):
                continue

            quando = self.ler_data(lembrete.get("quando"))
            if quando and agora >= quando:
                lembrete["entregue"] = True
                mensagens.append(f"Lembrete: {lembrete.get('texto', 'você pediu para lembrar')}")

        self.limpar_lembretes_antigos()
        return mensagens

    def verificar_pomodoro(self):
        pomodoro = self.dados.get("pomodoro", {})
        if not pomodoro.get("ativo"):
            return None

        fim = self.ler_data(pomodoro.get("fim"))
        if not fim or datetime.now() < fim:
            return None

        if pomodoro.get("fase") == "foco":
            pausa = int(pomodoro.get("pausa_minutos", 5))
            pomodoro["fase"] = "pausa"
            pomodoro["fim"] = (datetime.now() + timedelta(minutes=pausa)).isoformat(timespec="seconds")
            return f"Pomodoro concluído! Pausa de {pausa} minutos agora."

        pomodoro["ativo"] = False
        pomodoro["fase"] = ""
        pomodoro["fim"] = ""
        return "Pausa finalizada. Quer começar outro foco?"

    def verificar_app(self, app):
        agora = datetime.now()
        app_anterior = self.dados.get("app_atual", "")

        if app != app_anterior:
            self.dados["app_atual"] = app
            self.dados["inicio_app"] = agora.isoformat(timespec="seconds")
            self.dados["ultimo_aviso_app"] = ""
            return None

        regra = AVISOS_POR_APP.get(app)
        if not regra:
            return None

        inicio = self.ler_data(self.dados.get("inicio_app")) or agora
        ultimo_aviso = self.ler_data(self.dados.get("ultimo_aviso_app"))
        tempo_no_app = (agora - inicio).total_seconds()
        tempo_desde_aviso = (agora - ultimo_aviso).total_seconds() if ultimo_aviso else None

        if tempo_no_app < regra["segundos"]:
            return None

        if tempo_desde_aviso is not None and tempo_desde_aviso < INTERVALO_REPETIR_AVISO:
            return None

        self.dados["ultimo_aviso_app"] = agora.isoformat(timespec="seconds")
        return regra["mensagem"]

    def limpar_lembretes_antigos(self):
        lembretes = self.dados.get("lembretes", [])
        entregues = [lembrete for lembrete in lembretes if lembrete.get("entregue")]
        pendentes = [lembrete for lembrete in lembretes if not lembrete.get("entregue")]
        self.dados["lembretes"] = entregues[-20:] + pendentes

    def texto_status(self, app):
        partes = []
        partes.append("Automações ligadas." if self.dados.get("ativo", True) else "Automações pausadas.")

        pendentes = [item for item in self.dados.get("lembretes", []) if not item.get("entregue")]
        partes.append(f"Lembretes pendentes: {len(pendentes)}.")

        pomodoro = self.dados.get("pomodoro", {})
        if pomodoro.get("ativo"):
            fim = self.ler_data(pomodoro.get("fim"))
            minutos = max(0, int((fim - datetime.now()).total_seconds() // 60)) if fim else 0
            partes.append(f"Pomodoro em {pomodoro.get('fase', 'foco')}: {minutos} min restantes.")

        if app:
            partes.append(f"App ativo: {app}.")

        return " ".join(partes)

    def texto_ajuda(self):
        return (
            "Comandos: lembrar de beber água em 10 minutos; "
            "pomodoro 25; status; pausar automações; abrir github.com; "
            "abrir chrome; nova aba; clicar em 450, 300; digitar oi; fechar."
        )

    def ler_data(self, valor):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None

    def normalizar_texto(self, texto):
        texto = texto.strip().lower()
        texto = unicodedata.normalize("NFD", texto)
        return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")

    def texto_tempo(self, quantidade, unidade):
        unidade = unidade.lower()

        if unidade.startswith("s"):
            nome = "segundo" if quantidade == 1 else "segundos"
        elif unidade.startswith("h"):
            nome = "hora" if quantidade == 1 else "horas"
        else:
            nome = "minuto" if quantidade == 1 else "minutos"

        return f"{quantidade} {nome}"

    def resposta(self, entendido, mensagem, acao=None):
        return {
            "entendido": entendido,
            "mensagem": mensagem,
            "acao": acao,
        }
