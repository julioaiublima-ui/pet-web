import unittest
from unittest.mock import patch

from systems.app_detection import detectar_app


class FakeWindow:
    def __init__(self, title):
        self._title = title

    def title(self):
        return self._title


class TestDeteccaoApp(unittest.TestCase):
    @patch("systems.app_detection.gw.getActiveWindow")
    def test_detecta_codigo_ativo(self, mock_get_active_window):
        mock_get_active_window.return_value = FakeWindow("Visual Studio Code - projeto")

        self.assertEqual(detectar_app(), "Code")

    @patch("systems.app_detection.gw.getActiveWindow")
    def test_detecta_chrome_ativo(self, mock_get_active_window):
        mock_get_active_window.return_value = FakeWindow("Google Chrome")

        self.assertEqual(detectar_app(), "Chrome")

    @patch("systems.app_detection.gw.getActiveWindow")
    def test_retorna_vazio_quando_aplicativo_nao_foi_reconhecido(self, mock_get_active_window):
        mock_get_active_window.return_value = FakeWindow("Terminal do Windows")

        self.assertEqual(detectar_app(), "")


if __name__ == "__main__":
    unittest.main()
