import unittest

from systems.rag_system import ConfiguracaoRAG, RAGMemoria


class TestRAGMemoria(unittest.TestCase):
    def setUp(self):
        self.historico = [
            {
                "texto": "lembrar de beber agua",
                "resposta": "Vou lembrar você.",
                "app": "Code",
            },
            {
                "texto": "qual a capital da França",
                "resposta": "Paris.",
                "app": "Chrome",
            },
        ]

    def test_recupera_memoria_relevante(self):
        rag = RAGMemoria()

        resultados = rag.recuperar(self.historico, "beber agua")

        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["texto"], "lembrar de beber agua")
        self.assertGreaterEqual(resultados[0]["score"], 0.40)

    def test_top_k_e_configuravel(self):
        rag = RAGMemoria(ConfiguracaoRAG(top_k=1, score_minimo=0.0))

        resultados = rag.recuperar(self.historico, "a")

        self.assertEqual(len(resultados), 1)

    def test_ignora_entradas_invalidas(self):
        rag = RAGMemoria()

        resultados = rag.recuperar([None, "texto", {"texto": 123}], "teste")

        self.assertEqual(resultados, [])


if __name__ == "__main__":
    unittest.main()
