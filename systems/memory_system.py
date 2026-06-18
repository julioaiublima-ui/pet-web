import json
from pathlib import Path
from systems.memory_rag_system import (
    carregar_memoria,
    salvar_memoria,
    montar_contexto_rag,
    registrar_interacao,
    detectar_contexto,
    recuperar_contexto_rag
)


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_MEMORIA = PASTA_PROJETO / "memory.json"
LIMITE_HISTORICO = 200  # Aumentado para manter mais histórico


def montar_historico(memoria, limite=5):
    """Mantém compatibilidade - usa RAG para recuperação"""
    return montar_contexto_rag("", "geral", limite)


# Exportar funções RAG para uso direto
__all__ = [
    "carregar_memoria",
    "salvar_memoria",
    "registrar_interacao",
    "montar_historico",
    "montar_contexto_rag",
    "recuperar_contexto_rag",
    "detectar_contexto"
]
