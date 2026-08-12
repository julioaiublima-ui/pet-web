import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from systems.mood_system import AutomacoesMarcy


class TestMoodConfirmation(unittest.TestCase):
    def test_abertura_pede_confirmacao_e_confirma(self):
        with TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "automacoes.json"
            a = AutomacoesMarcy(arquivo)

            res = a.executar_comando("abrir github.com", app="")
            self.assertTrue(res["entendido"])
            # should be awaiting confirmation
            self.assertTrue(a.tem_acao_pendente())

            # user confirms
            resp2 = a.executar_comando("sim", app="")
            self.assertTrue(resp2["entendido"])
            self.assertIn("Abrindo", resp2["mensagem"])
            self.assertFalse(a.tem_acao_pendente())


if __name__ == "__main__":
    unittest.main()
