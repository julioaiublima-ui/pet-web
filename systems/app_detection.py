import pygetwindow as gw


APPS_RECONHECIDOS = {
    "code": "Code",
    "chrome": "Chrome",
    "spotify": "Spotify",
    "discord": "Discord",
    "steam": "Steam",
    "youtube": "YouTube",
    "github": "GitHub",
}


def detectar_app():
    titulo = obter_titulo_janela_ativa()

    for trecho, nome_app in APPS_RECONHECIDOS.items():
        if trecho in titulo:
            return nome_app

    return ""


def obter_titulo_janela_ativa():
    try:
        janela = gw.getActiveWindow()
    except Exception:
        return ""

    if not janela:
        return ""

    titulo = janela.title() if callable(janela.title) else janela.title
    return titulo.lower() if titulo else ""
