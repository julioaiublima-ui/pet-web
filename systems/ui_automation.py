import os
import subprocess

TECLAS_PERMITIDAS = {
    "enter",
    "esc",
    "escape",
    "tab",
    "space",
    "backspace",
    "delete",
    "up",
    "down",
    "left",
    "right",
}

ATALHOS_PERMITIDOS = {
    "nova_aba": ("command", "t"),
    "fechar_aba": ("command", "w"),
    "recarregar": ("command", "r"),
    "proxima_aba": ("ctrl", "tab"),
    "aba_anterior": ("ctrl", "shift", "tab"),
}


def is_enabled():
    return os.environ.get("MARCY_ENABLE_UI_AUTOMATION", "0") == "1"


def _bloqueio_automacao():
    return False, "Automação de UI está desabilitada (defina MARCY_ENABLE_UI_AUTOMATION=1)."


def _pyautogui_available():
    try:
        import pyautogui  # noqa: F401
        return True
    except Exception:
        return False


def open_app(app_name):
    """Open an application by name on macOS using `open -a`.

    Returns (ok: bool, message: str)
    """
    if not is_enabled():
        return _bloqueio_automacao()

    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return True, f"Abri {app_name}."
    except Exception as e:
        return False, f"Falha ao abrir {app_name}: {e}"


def click(x, y):
    if not is_enabled():
        return _bloqueio_automacao()

    if not _pyautogui_available():
        return False, "pyautogui não está disponível. Instale com pip install pyautogui."

    import pyautogui

    try:
        pyautogui.click(x=int(x), y=int(y))
        return True, f"Clique enviado em ({x},{y})."
    except Exception as e:
        return False, f"Falha ao clicar: {e}"


def type_text(text):
    if not is_enabled():
        return _bloqueio_automacao()

    if not _pyautogui_available():
        return False, "pyautogui não está disponível. Instale com pip install pyautogui."

    import pyautogui

    try:
        pyautogui.write(str(text))
        return True, "Texto digitado."
    except Exception as e:
        return False, f"Falha ao digitar: {e}"


def press_key(key):
    tecla = str(key or "").strip().lower()
    if tecla == "escape":
        tecla = "esc"

    if tecla not in TECLAS_PERMITIDAS:
        return False, f"Tecla não permitida: {key}"

    if not is_enabled():
        return _bloqueio_automacao()

    if not _pyautogui_available():
        return False, "pyautogui não está disponível. Instale com pip install pyautogui."

    import pyautogui

    try:
        pyautogui.press(tecla)
        return True, f"Tecla {tecla} enviada."
    except Exception as e:
        return False, f"Falha ao pressionar tecla: {e}"


def hotkey(nome_atalho):
    nome = str(nome_atalho or "").strip().lower()
    teclas = ATALHOS_PERMITIDOS.get(nome)

    if not teclas:
        return False, f"Atalho desconhecido: {nome_atalho}"

    if not is_enabled():
        return _bloqueio_automacao()

    if not _pyautogui_available():
        return False, "pyautogui não está disponível. Instale com pip install pyautogui."

    import pyautogui

    try:
        pyautogui.hotkey(*teclas)
        return True, "Atalho enviado."
    except Exception as e:
        return False, f"Falha ao enviar atalho: {e}"


def execute_action(acao):
    """Executa uma ação de automação simples definida como dicionário.

    Suporta tipos:
      - abrir_app: {"tipo":"abrir_app","app":"Nome do App"}
      - clicar: {"tipo":"clicar","x":123,"y":456}
      - digitar: {"tipo":"digitar","texto":"oi"}
      - pressionar: {"tipo":"pressionar","tecla":"enter"}
      - atalho: {"tipo":"atalho","atalho":"nova_aba"}

    Retorna (ok: bool, mensagem: str)
    """
    if not isinstance(acao, dict):
        return False, "Ação inválida"

    tipo = acao.get("tipo")
    if tipo == "abrir_app":
        return open_app(acao.get("app", ""))

    if tipo == "clicar":
        return click(acao.get("x", 0), acao.get("y", 0))

    if tipo == "digitar":
        return type_text(acao.get("texto", ""))

    if tipo == "pressionar":
        return press_key(acao.get("tecla", ""))

    if tipo == "atalho":
        return hotkey(acao.get("atalho", ""))

    return False, "Tipo de ação desconhecido"
