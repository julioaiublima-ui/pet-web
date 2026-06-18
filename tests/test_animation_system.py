import tempfile
import unittest
from pathlib import Path

from systems.animation_system import carregar_imagens, proximo_frame


class TestCarregarImagens(unittest.TestCase):
    def test_carregar_imagens_gera_fallback_quando_sprite_esta_vazio(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            (base / "sprites" / "idle").mkdir(parents=True)
            (base / "sprites" / "idle" / "idle_1.png").write_bytes(b"")

            imagens = carregar_imagens(base, 50)

            self.assertGreater(len(imagens), 0)

    def test_proximo_frame_suporta_sub_idle(self):
        self.assertEqual(proximo_frame("idle_glasses", 0), "idle_glasses_1")
        self.assertEqual(proximo_frame("idle_glasses", 3), "idle_glasses_1")


if __name__ == "__main__":
    unittest.main()
