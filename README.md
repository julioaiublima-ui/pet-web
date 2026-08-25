Este script usa `uv` com Python 3.13 e instala as dependencias temporarias `pillow`, `pygetwindow`, `pyautogui` e `pyobjc-framework-Quartz`, porque o Python da Apple pode apresentar erro ao criar janelas Tkinter.
# Marcy Desktop Companion

Uma personagem desktop leve baseada na Marcy Wu, de Amphibia. A Marcy anda pela tela, anima, observa o aplicativo ativo e responde usando uma IA local com Ollama.

## Stack

- Python 3
- Tkinter
- Pillow
- pygetwindow
- Ollama com `gemma3:1b`
- Memória local em JSON

## Estrutura do projeto

```text
pet-web/
├── marcy_pet.py
├── marcy_ai.py
├── ollama_helper.py
├── memory.json
├── requirements.txt
├── README.md
│
├── sprites/
│   ├── idle/
│   ├── walk/
│   ├── talking/
│   ├── thinking/
│   ├── observing/
│   └── emotions/
│
├── systems/
│   ├── app_detection.py
│   ├── memory_system.py
│   ├── mood_system.py
│   └── animation_system.py
│
└── assets/
    └── ui/
```

## Como usar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Garanta que o Ollama esteja instalado e com o modelo baixado:

```bash
ollama pull gemma3:1b
```

3. Deixe o Ollama rodando.

4. Execute a Marcy:

```bash
python3 marcy_pet.py
```

No macOS, se o Tkinter do Python do sistema falhar ao abrir janela, use o script:

```bash
./run_marcy.sh
```

Por padrao, a janela usa um fundo claro normal porque algumas versoes do Tk no macOS exibem `systemTransparent` como um retangulo preto. A transparencia experimental pode ser testada com:

```bash
MARCY_TRANSPARENTE=1 ./run_marcy.sh
```

Esse script usa `uv` com Python 3.13 e instala as dependencias temporarias `pillow`, `pygetwindow` e `pyobjc-framework-Quartz`, porque o Python da Apple pode apresentar erro ao criar janelas Tkinter.

## Automacoes interativas

A janela da Marcy tem um campo de texto para comandos. Exemplos:

```text
lembrar de beber agua em 10 minutos
pomodoro 25
status
pausar automacoes
ativar automacoes
abrir github.com
fechar
```

Quando um comando nao e reconhecido como automacao, ele e enviado para o Ollama e a Marcy responde como conversa normal.

Para conversar, clique no campo `fale com a Marcy...`, escreva a mensagem e pressione Enter. O Ollama precisa estar aberto para gerar a resposta.

## Arquivos principais

- `marcy_pet.py`: janela Tkinter, movimento, animacao, fala e deteccao de apps.
- `marcy_ai.py`: prompt, personalidade da Marcy e fluxo de resposta.
- `ollama_helper.py`: chamada HTTP para a API local do Ollama.
- `memory.json`: historico de interacoes da Marcy.
- `requirements.txt`: dependencias Python do projeto.
- `automacoes.json`: estado local das automacoes criado em tempo de execucao.
- `run_marcy.sh`: atalho para rodar no macOS usando `uv`.
- `sprites/`: pasta esperada para os sprites da personagem.
- `assets/ui/`: espaco para imagens e elementos visuais da interface.
- `systems/app_detection.py`: deteccao do app ativo.
- `systems/memory_system.py`: leitura, escrita e formatacao da memoria.
- `systems/mood_system.py`: comandos, lembretes, Pomodoro, regras por app ativo e acoes confirmadas.
- `systems/animation_system.py`: carregamento de sprites e selecao de frames.

## Sprites PNG ou GIF

Cada estado pode usar um GIF animado com o mesmo nome do estado. Por exemplo:

```text
sprites/
├── idle/idle.gif
├── walk/walk.gif
├── talking/talking.gif
├── thinking/thinking.gif
└── observing/observing.gif
```

Quando existe um GIF valido, todos os frames dele sao reproduzidos automaticamente. Se o GIF nao existir, a Marcy tenta carregar GIFs individuais `estado_1.gif`, `estado_2.gif` e usa um placeholder quando eles estiverem ausentes ou vazios.

## O que foi feito ate agora

### Base do pet

- Criada a janela desktop da Marcy usando Tkinter.
- Adicionado movimento automatico pela tela.
- Adicionada animacao por estado com suporte a GIFs `idle`, `walk`, `talking`, `thinking` e `observing`.
- Adicionado fallback visual com o texto "Marcy" quando os sprites ainda nao existem.
- Corrigida a deteccao de aplicativo ativo no `marcy_pet.py`.
- Adicionados apps reconhecidos: VS Code, Chrome, Spotify, Discord, Steam, YouTube e GitHub.
- Separada a logica de animacao em `systems/animation_system.py`.
- Separada a deteccao de apps em `systems/app_detection.py`.

### IA local com Ollama

- Substituida a IA simples baseada em palavras-chave por chamada local ao Ollama.
- Configurado o modelo `gemma3:1b`.
- Mantida a funcao `responder(texto, app)` para compatibilidade com `marcy_pet.py`.
- Adicionado prompt para a Marcy responder em portugues brasileiro, com frases curtas e personalidade curiosa.
- Adicionado uso das ultimas 5 interacoes do `memory.json` como contexto.
- Adicionado tratamento de erro quando o Ollama nao esta acessivel.
- Ajustada a chamada ao Ollama para rodar em thread e nao travar a janela.
- Criado `ollama_helper.py` para concentrar a chamada para a API do Ollama.
- Separado o sistema de memoria em `systems/memory_system.py`.

### Execucao no macOS

- Identificado problema no Tkinter do Python do sistema da Apple.
- Criado `run_marcy.sh` para rodar a Marcy com Python 3.13 via `uv`.
- Adicionadas dependencias temporarias no script: `pillow`, `pygetwindow` e `pyobjc-framework-Quartz`.
- Testado que a janela Tkinter abre usando o caminho do `uv`.

### Automacoes interativas

- Movido o sistema dinamico para `systems/mood_system.py`.
- Adicionado campo de texto na janela da Marcy para comandos do usuario.
- Adicionados lembretes com tempo relativo, como `lembrar de beber agua em 10 minutos`.
- Adicionado Pomodoro basico com foco e pausa, como `pomodoro 25`.
- Adicionado comando `status` para mostrar automacoes, lembretes e app ativo.
- Adicionados comandos para pausar e ativar automacoes.
- Adicionada confirmacao antes de abrir sites.
- Adicionado comando para fechar a Marcy pela propria janela.
- Adicionados avisos automaticos por tempo em alguns apps.
- Adicionado `automacoes.json` ao `.gitignore`, pois ele guarda estado local criado em tempo de execucao.

### Documentacao e GitHub

- Atualizado o README com instrucoes de uso, comandos e pendencias.
- Organizada a estrutura de pastas com `systems/`, `assets/ui/` e subpastas de `sprites/`.
- Criado `requirements.txt` com as dependencias do projeto.
- Criado commit local com a integracao do Ollama.
- Tentado envio para o GitHub, mas o push ficou bloqueado porque o GitHub ainda nao esta autenticado nesse Mac.

## Estado atual

- A chamada ao Ollama com `gemma3:1b` foi testada.
- O Python do `uv` conseguiu abrir uma janela Tkinter.
- A Marcy roda pelo comando `./run_marcy.sh`.
- A Marcy aceita comandos por texto na propria janela.
- A pasta `sprites/` possui GIFs de idle e caminhada; o arquivo de caminhada pode ser separado em `walk-direita.gif` e `walk-esquerda.gif`.

## O que falta para finalizar

- Adicionar sprites reais em PNG ou GIF, por exemplo:
  - `sprites/idle/idle.gif` (GIF animado preferencial)
  - `sprites/idle/idle_1.png`
  - `sprites/idle/idle_2.png`
  - `sprites/walk/walk_1.png`
  - `sprites/walk/walk_2.png`
- Criar sprites extras para `talking`, `thinking`, `observing` e emocoes.
- Melhorar a interface visual do campo de comandos.
- Melhorar a interface de fala para textos maiores.
- Criar menu de contexto para pausar, fechar e mudar configuracoes.
- Limitar o tamanho do `memory.json` para ele nao crescer para sempre.
- Expandir automacoes para horarios exatos, lista de tarefas e rotinas personalizadas.
- Testar melhor em Windows e macOS.
- Opcional: empacotar o projeto como app executavel.

## Enviar para o GitHub

Se o remoto ja estiver configurado:

```bash
git add README.md requirements.txt marcy_ai.py marcy_pet.py ollama_helper.py systems/
git commit -m "Organize Marcy project structure"
git push origin master
```
