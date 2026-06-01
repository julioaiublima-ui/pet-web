# Marcy Desktop Companion — AGENTS.md

## Visão Geral
Desktop pet da Marcy Wu (Amphibia). Uma personagem que anda pela tela, anima, fala e reage ao usuário usando Python + Tkinter.

## Stack
- Python 3
- Tkinter (GUI)
- Pillow (imagens/sprites)
- pygetwindow (detecção de apps ativos)
- pyautogui, psutil (suporte)

## Estrutura
- `marcy_pet.py` — Classe `MarcyPet` (Tkinter), lógica de movimento, animação, detecção de app
- `marcy_ai.py` — IA simples com respostas baseadas em keywords + memória JSON
- `memory.json` — Histórico de interações (`{"historico": []}`)
- `sprites/` — Sprites por estado: `idle/`, `walk/`, `talking/`, `thinking/`, `observing/`, `emotions/`

## Convenções
- Código em português (variáveis, comentários, nomes de função)
- Respostas da IA em português com emojis
- Memória persistida em JSON (`carregar_memoria` / `salvar_memoria`)

## Estados do Pet
- `idle` — parado, sprites `idle_1.png`, `idle_2.png`
- `walk` — andando, sprites `walk_1.png`, `walk_2.png`
- Outros: `talking`, `thinking`, `observing` (emotions/)

## Padrões
- `self.root.after(ms, callback)` para loop principal (não usar `time.sleep`)
- Sprites redimensionadas para 50x50 com `.resize((50, 50))`
- Detecção de app: `gw.getActiveWindow().title`
- IA: `marcy_ai.responder(texto, app)` retorna string
- Chance de fala: ~10% a cada tick (`random.random() < 0.1`)

## Comandos
```bash
pip install pygetwindow psutil pyautogui pillow
python marcy_pet.py
```

## Bugs Conhecidos
- `move()` tem bloco solto fora do método (linha 69-72) que causa `SyntaxError`
- `animate()` tenta `self.images("walk_1", None)` com parênteses em vez de colchetes
- Chamada duplicada de `canvas.itemconfig` no `animate()`
