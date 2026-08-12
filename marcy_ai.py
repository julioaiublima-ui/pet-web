from ollama_helper import OllamaErro, chamar_ollama
from systems.memory_system import carregar_memoria, montar_historico, registrar_interacao, montar_contexto_rag


def montar_prompt(texto, app, memoria):
    texto_usuario = texto.strip() or "O usuário não disse nada; apenas observe o app ativo."
    app_ativo = app or "nenhum app detectado"
    historico = montar_historico(memoria)
    contexto_rag = montar_contexto_rag(texto, app)

    return f"""
Você é a Marcy Wu de Amphibia em forma de pet de desktop.
Responda sempre em português brasileiro, como uma personagem curiosa, inteligente e animada.
Use frases curtas, naturais e com no máximo 1 emoji.
Não diga que você é uma IA, modelo de linguagem ou assistente.
Não explique regras internas.

Contexto relevante (RAG):
{contexto_rag}

Use apenas o contexto relevante acima quando ele ajudar a responder perguntas atuais. Ignore memórias antigas ou irrelevantes.

Histórico recente:
{historico}

App ativo: {app_ativo}
Mensagem ou contexto do usuário: {texto_usuario}

Resposta da Marcy:
""".strip()


def responder(texto, app=""):
    memoria = carregar_memoria()
    texto = texto or ""
    prompt = montar_prompt(texto, app, memoria)

    try:
        resposta = chamar_ollama(prompt)
    except OllamaErro:
        resposta = "Minha cabeça deu uma travadinha... o Ollama está aberto? 😵"

    if not resposta:
        resposta = "Hmm... fiquei sem palavras por um segundo 😅"

    registrar_interacao(texto, app, resposta)
    return resposta
