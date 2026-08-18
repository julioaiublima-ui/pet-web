# Assistente de Voz e Chrome

Este modulo adiciona um agente LiveKit + OpenAI Realtime com uma ferramenta de automacao visual do Google Chrome via `browser-use`.

Nota tecnica: o prompt original cita `MultimodalAgent`, mas a API atual do LiveKit Agents usa `AgentSession` com `openai.realtime.RealtimeModel`. O arquivo [jarvis_assistant.py](/Users/juliothiago/Downloads/pet-web/jarvis_assistant.py) segue esse caminho moderno.

## 1. Instalar no Mac

```bash
cd /Users/juliothiago/Downloads/pet-web
brew update
brew install uv
uv venv --python 3.12 .venv-jarvis
source .venv-jarvis/bin/activate
uv pip install -r requirements-jarvis.txt
python -m playwright install chromium
```

Para instalar servidor e CLI do LiveKit:

```bash
brew install livekit livekit-cli
```

O Browser Use tambem recomenda este instalador quando `uv` estiver disponivel:

```bash
uvx browser-use install
```

No macOS, conceda permissao de Microfone ao Terminal/VS Code. Para automacao visual mais ampla, tambem pode ser necessario liberar Acessibilidade e Gravacao de Tela em Ajustes do Sistema > Privacidade e Seguranca.

## 2. Configurar chaves

Crie o arquivo local:

```bash
cp .env.example .env
```

Preencha:

```bash
OPENAI_API_KEY=sk-proj-sua-chave
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

A chave da OpenAI fica em [platform.openai.com/api-keys](https://platform.openai.com/api-keys). Para LiveKit local, `livekit-server --dev` usa `devkey` e `secret`. Para LiveKit Cloud, rode:

```bash
lk cloud auth
lk app env -w
```

O modelo default no `.env.example` e `gpt-4o-realtime-preview`, que corresponde ao GPT-4o Realtime do prompt. A documentacao atual da OpenAI lista modelos realtime mais novos, entao voce pode trocar `JARVIS_REALTIME_MODEL` para `gpt-realtime` ou `gpt-realtime-2.1` se sua conta tiver acesso.

## 3. Rodar e testar

Teste rapido sem servidor LiveKit externo:

```bash
source .venv-jarvis/bin/activate
python jarvis_assistant.py console
```

Modo texto, util para depurar sem microfone:

```bash
python jarvis_assistant.py console --text
```

Teste com servidor LiveKit local:

```bash
livekit-server --dev
```

Em outro terminal:

```bash
source .venv-jarvis/bin/activate
python jarvis_assistant.py dev
```

Para conectar um cliente WebRTC local, gere um token para uma sala:

```bash
lk token create \
  --api-key devkey \
  --api-secret secret \
  --join \
  --room jarvis-lab \
  --identity operador
```

Use `ws://localhost:7880`, sala `jarvis-lab` e esse token em um cliente LiveKit. O modo `console` continua sendo o caminho mais rapido para validar audio local no Mac.

## Fontes

- [OpenAI Realtime and audio](https://developers.openai.com/api/docs/guides/realtime)
- [OpenAI GPT-4o Realtime model](https://developers.openai.com/api/docs/models/gpt-4o-realtime-preview)
- [LiveKit OpenAI Realtime plugin](https://docs.livekit.io/agents/models/realtime/plugins/openai/)
- [LiveKit Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai/)
- [LiveKit local server](https://docs.livekit.io/transport/self-hosting/local/)
- [Browser Use open-source quickstart](https://docs.browser-use.com/open-source/quickstart)
- [Browser Use browser parameters](https://docs.browser-use.com/open-source/customize/browser/all-parameters)
