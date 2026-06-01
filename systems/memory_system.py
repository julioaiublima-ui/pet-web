import json
from pathlib import Path


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_MEMORIA = PASTA_PROJETO / "memory.json"


def carregar_memoria(caminho=ARQUIVO_MEMORIA):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            memoria = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        memoria = {"historico": []}

    if "historico" not in memoria:
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
        texto = item.get("texto") or "observação silenciosa"
        resposta = item.get("resposta") or ""
        linhas.append(f"Usuário: {texto}\nMarcy: {resposta}")

    return "\n".join(linhas)


def registrar_interacao(texto, app, resposta):
    memoria = carregar_memoria()
    memoria["historico"].append({
        "texto": (texto or "").lower(),
        "app": app,
        "resposta": resposta,
    })
    salvar_memoria(memoria)
