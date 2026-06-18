import json
import re
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
        texto_normalizado = texto_original.lower()

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

        abertura = self.tentar_preparar_abertura(texto_original)
        if abertura:
            return abertura

        if texto_normalizado in ("sair", "fechar", "tchau"):
            return self.resposta(True, "Tá bom, vou descansar um pouquinho.", {"tipo": "fechar"})

        return self.resposta(False, "")

    def responder_acao_pendente(self, texto):
        acao = self.dados.get("acao_pendente")
        if not acao:
            return None

        if texto in ("sim", "s", "pode", "confirmar", "confirma"):
            self.dados["acao_pendente"] = None
            self.salvar_dados()

            if acao.get("tipo") == "abrir_url":
                url = acao.get("url", "")
                return self.resposta(True, f"Abrindo {url}", acao)

        if texto in ("nao", "não", "n", "cancelar"):
            self.dados["acao_pendente"] = None
            self.salvar_dados()
            return self.resposta(True, "Beleza, não vou abrir nada.")

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

    def tentar_preparar_abertura(self, texto):
        resultado = re.search(r"\babrir\s+(.+)", texto, re.IGNORECASE)
        if not resultado:
            return None

        destino = resultado.group(1).strip().lower()
        atalhos = {
            "github": "https://github.com",
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "ollama": "https://ollama.com",
        }
        url = atalhos.get(destino, destino)

        if "." not in url and not url.startswith(("http://", "https://")):
            return self.resposta(True, "Consigo abrir sites. Me diga algo tipo: abrir github.com")

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        acao = {"tipo": "abrir_url", "url": url}
        self.dados["acao_pendente"] = acao
        self.salvar_dados()

        return self.resposta(True, f"Quer que eu abra {url}? Responda sim ou não.")

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
            "pomodoro 25; status; pausar automações; abrir github.com; fechar."
        )

    def ler_data(self, valor):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None

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
