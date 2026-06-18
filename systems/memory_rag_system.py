"""
Sistema RAG (Retrieval-Augmented Generation) para Marcy Pet
Recuperação inteligente de contexto com busca semântica simples
"""
import json
import re
from pathlib import Path
from collections import defaultdict


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_MEMORIA = PASTA_PROJETO / "memory.json"
LIMITE_HISTORICO_TOTAL = 200
LIMITE_CONTEXTO_RAG = 10  # Quantidade de items a recuperar por contexto


# Temas de contexto para classificação automática
CONTEXTOS_PALAVRAS = {
    "programacao": ["código", "bug", "erro", "debug", "função", "variável", "python", "javascript", "html", "css", "git", "commit", "merge", "branch", "algoritmo", "loop", "array", "dicionário", "classe", "método", "import", "library", "package"],
    "pessoal": ["nome", "idade", "aniversário", "família", "amigo", "gostar", "preferir", "ama", "odeia", "hobby", "sport", "música", "filme", "série", "livro"],
    "trabalho": ["projeto", "reunião", "deadline", "cliente", "apresentação", "documento", "email", "tarefa", "equipe", "chefe", "colega", "entrega", "meeting", "meeting", "sprint", "backlog", "status", "relatório", "planejamento"],
    "criatividade": ["desenho", "desenhar", "art", "música", "musica", "canção", "canção", "poesia", "história", "historia", "criativo", "criar", "criando", "ideia", "inspiração", "inspiracao", "imaginação", "imaginacao", "escrever", "pintar"],
    "geral": []  # Fallback
}


def detectar_contexto(texto):
    """Detecta o contexto temático de um texto"""
    import re
    texto_lower = texto.lower()
    # Remove pontuação e divide em palavras
    palavras_texto = set(re.findall(r'\b\w+\b', texto_lower))
    
    pontuacao = defaultdict(int)
    
    for contexto, palavras in CONTEXTOS_PALAVRAS.items():
        if contexto == "geral":
            continue
        for palavra in palavras:
            # Busca por palavra completa, não substring
            if palavra in palavras_texto or palavra in texto_lower.split():
                pontuacao[contexto] += 1
    
    if pontuacao:
        return max(pontuacao, key=pontuacao.get)
    return "geral"


def calcular_relevancia(item_memoria, termo_busca, contexto_atual=None):
    """
    Calcula relevância de um item para recuperação RAG
    Leva em conta: similaridade de palavras, contexto, recenticidade relativa
    """
    texto_item = (item_memoria.get("texto", "") + " " + item_memoria.get("resposta", "")).lower()
    termo_lower = termo_busca.lower()
    
    # Score base: quantas palavras do termo_busca aparecem no item
    palavras_termo = termo_lower.split()
    matches = sum(1 for palavra in palavras_termo if palavra in texto_item and len(palavra) > 2)
    score = matches / max(len(palavras_termo), 1)
    
    # Boost para contexto similar
    contexto_item = item_memoria.get("contexto", "geral")
    if contexto_atual and contexto_item == contexto_atual:
        score *= 1.5
    
    # Leve preferência por respostas mais recentes (índice no histórico)
    # score *= (0.8 + 0.2 * (indice_normalizado))
    
    return score


def carregar_memoria(caminho=ARQUIVO_MEMORIA):
    """Carrega memória completa com estrutura RAG"""
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            memoria = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        memoria = {"historico": []}
    
    if "historico" not in memoria:
        memoria["historico"] = []
    
    # Garante que todos os items têm contexto
    for item in memoria["historico"]:
        if "contexto" not in item:
            item["contexto"] = detectar_contexto(item.get("texto", "") + " " + item.get("resposta", ""))
    
    return memoria


def salvar_memoria(memoria, caminho=ARQUIVO_MEMORIA):
    """Salva memória com limite total"""
    if "historico" in memoria:
        memoria["historico"] = memoria["historico"][-LIMITE_HISTORICO_TOTAL:]
    
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(memoria, arquivo, ensure_ascii=False, indent=2)


def recuperar_contexto_rag(termo_busca="", contexto_atual="geral", limite=LIMITE_CONTEXTO_RAG):
    """
    RAG: Recupera items relevantes de memória baseado em busca semântica
    Prioriza items relacionados ao contexto e tema da conversa
    """
    memoria = carregar_memoria()
    historico = memoria.get("historico", [])
    
    if not historico:
        return []
    
    # Calcula relevância de cada item
    items_com_score = []
    for idx, item in enumerate(historico):
        score = calcular_relevancia(item, termo_busca, contexto_atual)
        if score > 0:
            items_com_score.append((score, idx, item))
    
    # Ordena por relevância e retorna top-N
    items_ordenados = sorted(items_com_score, key=lambda x: x[0], reverse=True)
    return [item for _, _, item in items_ordenados[:limite]]


def montar_contexto_rag(termo_busca="", contexto_atual="geral", limite=5):
    """
    Monta contexto para o prompt usando RAG
    Retorna histórico estruturado com items mais relevantes
    """
    items_relevantes = recuperar_contexto_rag(termo_busca, contexto_atual, limite)
    
    if not items_relevantes:
        return "Sem conversas anteriores."
    
    linhas = []
    for item in items_relevantes:
        texto = item.get("texto") or "observação silenciosa"
        resposta = item.get("resposta") or ""
        # Marcar contexto para transparência
        contexto = item.get("contexto", "geral")
        linhas.append(f"Usuário: {texto}\nMarcy: {resposta} [{contexto}]")
    
    return "\n".join(linhas)


def registrar_interacao(texto, app, resposta):
    """Registra interação com contexto automático"""
    memoria = carregar_memoria()
    
    contexto = detectar_contexto(texto + " " + resposta)
    
    memoria["historico"].append({
        "texto": (texto or "").lower(),
        "app": app,
        "resposta": resposta,
        "contexto": contexto,
        "timestamp": None  # Pode adicionar timestamp se necessário
    })
    
    salvar_memoria(memoria)
