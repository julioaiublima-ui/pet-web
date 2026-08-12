import difflib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConfiguracaoRAG:
    top_k: int = 2
    score_minimo: float = 0.40
    peso_texto: float = 0.80
    peso_resposta: float = 0.20
    peso_app: float = 0.10


class RAGMemoria:
    def __init__(self, configuracao=None):
        self.configuracao = configuracao or ConfiguracaoRAG()

    def recuperar(self, historico, consulta, app=""):
        consulta_normalizada = self.normalizar(" ".join(filter(None, [consulta or "", app or ""])))
        candidatos = []

        for item in historico or []:
            if not isinstance(item, dict):
                continue

            texto = self.normalizar(item.get("texto"))
            resposta = self.normalizar(item.get("resposta"))
            app_memoria = self.normalizar(item.get("app"))
            score = self.calcular_score(
                consulta_normalizada,
                texto,
                resposta,
                app_memoria,
            )

            if score >= self.configuracao.score_minimo:
                candidatos.append({
                    "texto": item.get("texto"),
                    "resposta": item.get("resposta"),
                    "app": item.get("app"),
                    "score": score,
                })

        candidatos.sort(key=lambda item: item["score"], reverse=True)
        return candidatos[:max(0, self.configuracao.top_k)]

    def calcular_score(self, consulta, texto, resposta, app):
        score_texto = self.similaridade(consulta, texto)
        score_resposta = self.similaridade(consulta, resposta)
        score_app = self.similaridade(consulta, app)
        return (
            score_texto * self.configuracao.peso_texto
            + score_resposta * self.configuracao.peso_resposta
            + score_app * self.configuracao.peso_app
        )

    def montar_contexto(self, entradas):
        if not entradas:
            return "Sem memórias relevantes."

        linhas = []
        for entrada in entradas:
            score = f"{entrada['score']:.2f}"
            app = entrada.get("app") or ""
            texto = entrada.get("texto") or "observação silenciosa"
            resposta = entrada.get("resposta") or ""
            linhas.append(
                f"[score={score}] App: {app} | Usuário: {texto} -> Marcy: {resposta}"
            )
        return "\n".join(linhas)

    @staticmethod
    def normalizar(valor: Any):
        return str(valor or "").strip().lower()

    @staticmethod
    def similaridade(primeiro, segundo):
        if not primeiro or not segundo:
            return 0.0
        return difflib.SequenceMatcher(None, primeiro, segundo).ratio()
