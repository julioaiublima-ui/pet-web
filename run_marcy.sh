#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

UV_BIN="${UV_BIN:-uv}"
if ! command -v "$UV_BIN" >/dev/null 2>&1 && [ -x "$HOME/.local/bin/uv" ]; then
  UV_BIN="$HOME/.local/bin/uv"
fi

"$UV_BIN" run --python 3.13 --with pillow --with pygetwindow --with pyautogui --with pyobjc-framework-Quartz python marcy_pet.py
