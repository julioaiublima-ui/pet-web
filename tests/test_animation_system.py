import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from marcy_pet import direcao_horizontal
from systems.animation_system import carregar_imagens, duracao_frame, proximo_frame


class TestCarregarImagens(unittest.TestCase):
    def test_direcao_horizontal_acompanha_movimento_do_mouse(self):
        self.assertEqual(direcao_horizontal(10), 1)
        self.assertEqual(direcao_horizontal(-10), -1)
        self.assertEqual(direcao_horizontal(0), 0)

    def test_mover_funciona_para_direita_esquerda_e_para_quando_delta_zero(self):
        pet = SimpleNamespace(
            root=SimpleNamespace(
                winfo_screenwidth=lambda: 1000,
                winfo_screenheight=lambda: 800,
                geometry=lambda geometria: None,
            ),
            x=500,
            y=100,
            alvo_x=500,
            alvo_y=100,
            dx=0,
            dy=0,
            ultima_direcao_horizontal=1,
            estado="idle",
        )

        from marcy_pet import MarcyPet

        pet.alvo_x = 700
        MarcyPet.mover(pet)
        self.assertEqual((pet.x, pet.y, pet.dx, pet.dy, pet.estado), (510, 100, 1, 0, "walk_direita"))

        pet.alvo_x = 500
        MarcyPet.mover(pet)
        self.assertEqual((pet.x, pet.y, pet.dx, pet.dy, pet.estado), (500, 100, 0, 0, "idle"))

        pet.alvo_x = 700
        pet.alvo_y = 300
        MarcyPet.mover(pet)
        self.assertAlmostEqual(pet.x, 510, places=1)
        self.assertAlmostEqual(pet.y, 110, places=1)
        self.assertEqual((pet.dx, pet.dy, pet.estado), (1, 1, "walk_direita"))

        pet.alvo_x = pet.x
        pet.alvo_y = 40
        MarcyPet.mover(pet)
        self.assertAlmostEqual(pet.y, 100, places=1)
        self.assertEqual((pet.dx, pet.dy, pet.estado), (0, -1, "walk_direita"))

        pet.alvo_y = pet.y
        MarcyPet.mover(pet)
        self.assertEqual((pet.dx, pet.dy, pet.estado), (0, 0, "idle"))

    def test_carregar_imagens_le_todos_os_frames_de_um_gif(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            pasta_idle = base / "sprites" / "idle"
            pasta_idle.mkdir(parents=True)
            frames = [
                Image.new("RGBA", (10, 10), (255, 0, 0, 255)),
                Image.new("RGBA", (10, 10), (0, 255, 0, 255)),
                Image.new("RGBA", (10, 10), (0, 0, 255, 255)),
            ]
            frames[0].save(
                pasta_idle / "idle.gif",
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0,
            )

            imagens = carregar_imagens(base, 50)

            self.assertEqual(len([nome for nome in imagens if nome.startswith("idle_")]), 3)
            self.assertEqual(proximo_frame("idle", 2), "idle_3")
            self.assertEqual(duracao_frame("idle", 0), 100)

    def test_carregar_imagens_gera_fallback_quando_sprite_esta_vazio(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            (base / "sprites" / "idle").mkdir(parents=True)
            (base / "sprites" / "idle" / "idle-1.gif").write_bytes(b"")

            imagens = carregar_imagens(base, 50)

            self.assertGreater(len(imagens), 0)


if __name__ == "__main__":
    unittest.main()
