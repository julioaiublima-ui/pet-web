import json
import urllib.error
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_OLLAMA = "gemma3:1b"
TEMPO_LIMITE = 20


class OllamaErro(Exception):
    pass


def chamar_ollama(prompt):
    dados = {
        "model": MODELO_OLLAMA,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 60,
        },
    }

    requisicao = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(dados).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=TEMPO_LIMITE) as resposta_http:
            resposta_json = json.loads(resposta_http.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as erro:
        raise OllamaErro("Nao foi possivel chamar o Ollama.") from erro

    return resposta_json.get("response", "").strip()
