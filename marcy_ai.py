import random
import json

MEMORY_FILE = "memory.json"

def carregar_memoria():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def salvar_memoria(memoria):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memoria, f)

def responder(texto, app=""):

    memoria = carregar_memoria()

    texto = texto.lower()

    if "oi" in texto:
        resposta = random.choice([
            "Oi!! 😄",
            "Hey! Você voltou!",
            "Oi oi! O que tá fazendo?"
        ])

    elif "código" in texto:
        resposta = random.choice([
            "Você tá programando? 🤓",
            "Isso parece complicado 👀",
            "Posso tentar ajudar!"
        ])

    elif app == "Code":
        resposta = random.choice([
            "Programando de novo? 🤓",
            "Você passa bastante tempo no VS Code 👀"
        ])

    elif app == "Chrome":
        resposta = random.choice([
            "Pesquisando alguma coisa?",
            "Hmm... isso parece interessante 👀"
        ])

    else:
        resposta = random.choice([
            "Estou observando 👀",
            "Hmm... interessante 🤔",
            "Você parece ocupado hoje"
        ])

    memoria["historico"].append({
        "texto": texto,
        "resposta": resposta
    })

    salvar_memoria(memoria)

    return resposta