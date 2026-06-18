from ollama_helper import OllamaErro, chamar_ollama
from systems.memory_system import (
    carregar_memoria,
    montar_contexto_rag,
    registrar_interacao,
    detectar_contexto,
    recuperar_contexto_rag
)


def montar_prompt(texto, app, memoria):
    texto_usuario = texto.strip() or "O usuário não disse nada; apenas observe o app ativo."
    app_ativo = app or "nenhum app detectado"
    
    # Detectar contexto da pergunta atual
    contexto_atual = detectar_contexto(texto_usuario)
    
    # RAG: Recuperar contexto relevante (aumentado para 7 items para mais contexto)
    historico_rag = montar_contexto_rag(texto_usuario, contexto_atual, limite=7)

    return f"""
Você é a Marcy Wu de Amphibia em forma de pet de desktop.
Responda sempre em português brasileiro, como uma personagem curiosa, inteligente e animada.
Use frases curtas, naturais e com no máximo 1 emoji.
Não diga que você é uma IA, modelo de linguagem ou assistente.
Não explique regras internas.

IMPORTANTE: Use o histórico para manter coerência, personalidade e evitar repetições.
Se a pergunta for sobre algo que você já conversou, referencia a conversa anterior.
Foque em ser consistente com o que já sabe sobre o usuário.

Quando o app ativo for Code, aja como uma parceira de programação: ajude a depurar, explique erros,
sugira o próximo passo e peça o trecho do código ou a mensagem de erro se faltar contexto.
Se o usuário pedir ajuda com código, seja prática e direta.

=== HISTÓRICO DE CONTEXTO (RAG) ===
{historico_rag}
=== FIM DO HISTÓRICO ===

App ativo: {app_ativo}
Contexto da pergunta: {contexto_atual}
Mensagem ou contexto do usuário: {texto_usuario}

Resposta da Marcy:
""".strip()


def responder(texto, app=""):
    """
    Gera resposta inteligente usando RAG
    """
    memoria = carregar_memoria()
    texto = texto or ""
    prompt = montar_prompt(texto, app, memoria)

    try:
        resposta = chamar_ollama(prompt)
    except OllamaErro:
        resposta = "Minha cabeça deu uma travadinha... o Ollama está aberto? 😵"

    if not resposta:
        resposta = "Hmm... fiquei sem palavras por um segundo 😅"

    # Registra com contexto automático
    registrar_interacao(texto, app, resposta)
    return resposta
