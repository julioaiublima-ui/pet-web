import json
import tempfile
import unittest
from pathlib import Path

from systems.memory_rag_system import carregar_memoria, registrar_interacao, salvar_memoria


class TestMemorySystem(unittest.TestCase):
    def test_registrar_interacao_nao_salva_interacao_vazia(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho = Path(tmp_dir) / "memory.json"
            registrar_interacao("", "Code", "Observei! 🧐")
            memoria = carregar_memoria(caminho)
            self.assertEqual(memoria["historico"], [])

    def test_registrar_interacao_nao_salva_resposta_generica_sem_texto(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho = Path(tmp_dir) / "memory.json"
            # Pre-popula o arquivo para garantir que a função usa o caminho padrão quando chamado internamente
            caminho.write_text(json.dumps({"historico": []}, ensure_ascii=False), encoding="utf-8")

            from systems.memory_rag_system import ARQUIVO_MEMORIA
            # Temporariamente substituir o caminho global da memória para o teste
            original = ARQUIVO_MEMORIA
            try:
                from systems import memory_rag_system as sistema
                sistema.ARQUIVO_MEMORIA = caminho
                registrar_interacao("", "Code", "Minha cabeça deu uma travadinha... o Ollama está aberto? 😵")
                memoria = carregar_memoria(caminho)
                self.assertEqual(memoria["historico"], [])
            finally:
                from systems import memory_rag_system as sistema
                sistema.ARQUIVO_MEMORIA = original

    def test_salvar_memoria_limita_tamanho_historico(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho = Path(tmp_dir) / "memory.json"
            memoria = {"historico": [{"texto": f"mensagem {i}", "app": "Code", "resposta": "ok", "contexto": "programacao"} for i in range(250)]}
            salvar_memoria(memoria, caminho)
            with open(caminho, "r", encoding="utf-8") as arquivo:
                salvo = json.load(arquivo)
            self.assertEqual(len(salvo["historico"]), 200)


if __name__ == "__main__":
    unittest.main()
