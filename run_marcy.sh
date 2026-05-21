#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
uv run --python 3.13 --with pillow --with pygetwindow --with pyobjc-framework-Quartz python marcy_pet.py
