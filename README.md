# Marcy Desktop Companion

Uma personagem desktop leve para Windows, baseada em Marcy Wu, que anda pela tela, anima, fala e reage ao usuário.

## Como usar

1. Instale Python e as bibliotecas: `pip install pygetwindow psutil pyautogui pillow`
2. Adicione sprites em `sprites/` (idle_1.png, etc.)
3. Execute: `python marcy_pet.py`

## Enviar para o GitHub

1. Instale o Git no Windows.
2. No terminal, rode:
   ```bash
   git init
   git add .
   git commit -m "Marcy Desktop Companion"
   git remote add origin <URL-do-seu-repositório>
   git push -u origin main
   ```

Substitua `<URL-do-seu-repositório>` pela URL do repositório GitHub que você criou.

## Funcionalidades

- Movimento pela tela
- Animações por estado
- Detecção de apps abertos
- Respostas inteligentes leves
- Memória simples

## Melhorias futuras

- Seguir mouse
- Dormir quando inativo
- Mais emoções