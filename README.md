# Marcy Desktop Companion

Uma personagem desktop leve baseada na Marcy Wu, de Amphibia. A Marcy anda pela tela, anima, observa o aplicativo ativo e responde usando uma IA local com Ollama.

## Stack

- Python 3
- Tkinter
- Pillow
- pygetwindow
- Ollama com `gemma3:1b`
- Memória local em JSON

## Como usar

1. Instale as dependências:

```bash
pip install pygetwindow psutil pyautogui pillow
```

2. Garanta que o Ollama esteja instalado e com o modelo baixado:

```bash
ollama pull gemma3:1b
```

3. Deixe o Ollama rodando.

4. Execute a Marcy:

```bash
python marcy_pet.py
```

No macOS, se o Tkinter do Python do sistema falhar ao abrir janela, use o script:

```bash
./run_marcy.sh
```

Esse script usa `uv` com Python 3.13 e instala as dependencias temporarias `pillow`, `pygetwindow` e `pyobjc-framework-Quartz`, porque o Python da Apple pode apresentar erro ao criar janelas Tkinter.

## Arquivos principais

- `marcy_pet.py`: janela Tkinter, movimento, animacao, fala e deteccao de apps.
- `marcy_ai.py`: integracao com a API local do Ollama.
- `memory.json`: historico de interacoes da Marcy.
- `run_marcy.sh`: atalho para rodar no macOS usando `uv`.
- `sprites/`: pasta esperada para os sprites da personagem.

## Alteracoes feitas ate agora

- Substituida a IA simples por chamada local ao Ollama.
- Configurado o modelo `gemma3:1b`.
- Mantida a funcao `responder(texto, app)` para compatibilidade com `marcy_pet.py`.
- Adicionado prompt para a Marcy responder em portugues brasileiro, com frases curtas e personalidade curiosa.
- Adicionado uso das ultimas 5 interacoes do `memory.json` como contexto.
- Adicionado tratamento de erro quando o Ollama nao esta acessivel.
- Corrigida a deteccao de aplicativo ativo no `marcy_pet.py`.
- Adicionados apps reconhecidos: VS Code, Chrome, Spotify, Discord, Steam, YouTube e GitHub.
- Ajustada a chamada ao Ollama para rodar em thread e nao travar a janela.
- Melhorada a animacao com alternancia entre frames `idle` e `walk`.
- Adicionado fallback visual com texto "Marcy" quando os sprites ainda nao existem.
- Criado `run_marcy.sh` para contornar problema do Tkinter no Python do sistema no macOS.

## Estado atual

- A chamada ao Ollama com `gemma3:1b` foi testada.
- O Python do `uv` conseguiu abrir uma janela Tkinter.
- A Marcy roda pelo comando `./run_marcy.sh`.
- A pasta `sprites/` ainda nao possui os PNGs finais da personagem.

## O que falta para finalizar

- Adicionar sprites reais em:
  - `sprites/idle/idle_1.png`
  - `sprites/idle/idle_2.png`
  - `sprites/walk/walk_1.png`
  - `sprites/walk/walk_2.png`
- Criar sprites extras para `talking`, `thinking`, `observing` e emocoes.
- Melhorar a interface de fala para evitar textos longos demais na janela.
- Adicionar alguma forma de conversa direta com o usuario, como input por tecla ou menu.
- Criar controle para pausar/fechar a Marcy sem precisar encerrar pelo terminal.
- Limitar o tamanho do `memory.json` para ele nao crescer para sempre.
- Testar melhor em Windows e macOS.
- Opcional: empacotar o projeto como app executavel.

## Enviar para o GitHub

Se o remoto ja estiver configurado:

```bash
git add README.md marcy_ai.py marcy_pet.py run_marcy.sh
git commit -m "Add Ollama-powered Marcy desktop pet"
git push origin master
```
