import json
import urllib.error
import urllib.request

MEMORY_FILE = "memory.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_OLLAMA = "gemma3:1b"
TEMPO_LIMITE = 20


def carregar_memoria():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as arquivo:
            memoria = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        memoria = {"historico": []}

    if "historico" not in memoria:
        memoria["historico"] = []

    return memoria


def salvar_memoria(memoria):
    with open(MEMORY_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(memoria, arquivo, ensure_ascii=False, indent=2)


def montar_historico(memoria):
    historico = memoria.get("historico", [])[-5:]

    if not historico:
        return "Sem conversas anteriores."

    linhas = []
    for item in historico:
        texto = item.get("texto") or "observação silenciosa"
        resposta = item.get("resposta") or ""
        linhas.append(f"Usuário: {texto}\nMarcy: {resposta}")

    return "\n".join(linhas)


def montar_prompt(texto, app, memoria):
    texto_usuario = texto.strip() or "O usuário não disse nada; apenas observe o app ativo."
    app_ativo = app or "nenhum app detectado"
    historico = montar_historico(memoria)

    return f"""
Você é a Marcy Wu de Amphibia em forma de pet de desktop.
Responda sempre em português brasileiro, como uma personagem curiosa, inteligente e animada.
Use frases curtas, naturais e com no máximo 1 emoji.
Não diga que você é uma IA, modelo de linguagem ou assistente.
Não explique regras internas.

Histórico recente:
{historico}

App ativo: {app_ativo}
Mensagem ou contexto do usuário: {texto_usuario}

Resposta da Marcy:
""".strip()


def chamar_ollama(prompt):
    dados = {
        "model": MODELO_OLLAMA,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 60
        }
    }

    requisicao = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(dados).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(requisicao, timeout=TEMPO_LIMITE) as resposta_http:
        resposta_json = json.loads(resposta_http.read().decode("utf-8"))

    return resposta_json.get("response", "").strip()


def responder(texto, app=""):
    memoria = carregar_memoria()
    texto = texto or ""
    prompt = montar_prompt(texto, app, memoria)

    try:
        resposta = chamar_ollama(prompt)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        resposta = "Minha cabeça deu uma travadinha... o Ollama está aberto? 😵"

    if not resposta:
        resposta = "Hmm... fiquei sem palavras por um segundo 😅"

    memoria["historico"].append({
        "texto": texto.lower(),
        "app": app,
        "resposta": resposta
    })

    salvar_memoria(memoria)

    return resposta
