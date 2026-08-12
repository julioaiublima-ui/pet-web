import json
from pathlib import Path

from systems.rag_system import ConfiguracaoRAG, RAGMemoria


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_MEMORIA = PASTA_PROJETO / "memory.json"
LIMITE_HISTORICO = 100
CONFIGURACAO_RAG = ConfiguracaoRAG()


def carregar_memoria(caminho=ARQUIVO_MEMORIA):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            memoria = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        memoria = {"historico": []}

    if not isinstance(memoria, dict):
        memoria = {"historico": []}
    elif not isinstance(memoria.get("historico"), list):
        memoria["historico"] = []

    return memoria


def salvar_memoria(memoria, caminho=ARQUIVO_MEMORIA):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(memoria, arquivo, ensure_ascii=False, indent=2)


def montar_historico(memoria, limite=5):
    historico = memoria.get("historico", [])[-limite:]

    if not historico:
        return "Sem conversas anteriores."

    linhas = []
    for item in historico:
        if not isinstance(item, dict):
            continue
        texto = item.get("texto") or "observação silenciosa"
        resposta = item.get("resposta") or ""
        linhas.append(f"Usuário: {texto}\nMarcy: {resposta}")

    return "\n".join(linhas)


def recuperar_memoria_relevante(query, app=None, caminho=ARQUIVO_MEMORIA, top_k=CONFIGURACAO_RAG.top_k):
    memoria = carregar_memoria(caminho)
    configuracao = ConfiguracaoRAG(
        top_k=top_k,
        score_minimo=CONFIGURACAO_RAG.score_minimo,
        peso_texto=CONFIGURACAO_RAG.peso_texto,
        peso_resposta=CONFIGURACAO_RAG.peso_resposta,
        peso_app=CONFIGURACAO_RAG.peso_app,
    )
    rag = RAGMemoria(configuracao)
    return rag.recuperar(memoria.get("historico", []), query, app)


def montar_contexto_rag(query, app=None, caminho=ARQUIVO_MEMORIA, top_k=CONFIGURACAO_RAG.top_k):
    entradas = recuperar_memoria_relevante(query, app=app, caminho=caminho, top_k=top_k)
    return RAGMemoria(CONFIGURACAO_RAG).montar_contexto(entradas)


def registrar_interacao(texto, app, resposta):
    memoria = carregar_memoria()
    memoria["historico"].append({
        "texto": (texto or "").lower(),
        "app": app,
        "resposta": resposta,
    })
    memoria["historico"] = memoria["historico"][-LIMITE_HISTORICO:]
    salvar_memoria(memoria)
