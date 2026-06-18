# 🎛️ GUIA DE FINE-TUNING DO SISTEMA RAG

## 📋 Sumário Rápido

- **RAG é inteligente demais?** → Diminua `LIMITE_CONTEXTO_RAG` (de 7 para 5)
- **Marcy esquece demais?** → Aumente `LIMITE_CONTEXTO_RAG` (de 7 para 10)
- **Respostas genéricas demais?** → Aumente `LIMITE_HISTORICO_TOTAL` (de 200 para 300)
- **Movimento muito rápido?** → Aumente `INTERVALO_ATUALIZACAO` (de 300 para 400)
- **Movimento muito lento?** → Diminua `INTERVALO_ATUALIZACAO` (de 300 para 200)

---

## 🧩 PARÂMETRO: LIMITE_CONTEXTO_RAG

**Arquivo**: `systems/memory_rag_system.py` (linha ~13)

```python
LIMITE_CONTEXTO_RAG = 7  # Quantos items recuperar do histórico
```

### O que faz?
Define quantas interações anteriores são incluídas no prompt da Marcy.

### Ajustes por Cenário

| Valor | Caso de Uso | Prós | Contras |
|-------|-----------|------|---------|
| 3-4 | Respostas rápidas, menos contexto | Execução rápida, token menor | Pode esquecer contexto |
| **7** | **Padrão balanceado** | **Bom contexto, rápido** | **Nenhum** |
| 10 | Conversas longas, máximo contexto | Muito contexto, coerência | Token maior, + lento |
| 15+ | Histórico completo | Máxima consistência | Prompt muito grande |

### Exemplos

**Se quer Marcy mais "amnésica" (divertido):**
```python
LIMITE_CONTEXTO_RAG = 3
# Marcy vai esquecer conversas antigas mais rápido
# "Você já me contou sobre seu hobby?" → "Qual é meu hobby? 🤔"
```

**Se quer Marcy super consistente:**
```python
LIMITE_CONTEXTO_RAG = 12
# Marcy vai manter todo contexto
# "Você me disse que seu hobby é desenhar" → "Ah sim! Amo desenhar! 🎨"
```

---

## 🧩 PARÂMETRO: LIMITE_HISTORICO_TOTAL

**Arquivo**: `systems/memory_rag_system.py` (linha ~10)

```python
LIMITE_HISTORICO_TOTAL = 200  # Quantos items manter no arquivo
```

### O que faz?
Define tamanho máximo do arquivo `memory.json`. Quando atinge o limite, perde itens antigos.

### Ajustes por Cenário

| Valor | Caso | Prós | Contras |
|-------|------|------|---------|
| 50 | Teste, ambiente limitado | Arquivo pequeno | Perde contexto rápido |
| 100 | Conversa curtas | Rápido | Esquece fácil |
| **200** | **Padrão** | **Bom balanço** | **Nenhum** |
| 500 | Longo termo, máximo contexto | Memória muito completa | Arquivo grande |
| 1000+ | Pesquisa, análise | Histórico completo | Muito pesado |

### Exemplos

**Se quer resetar frequente (nova personalidade):**
```python
LIMITE_HISTORICO_TOTAL = 50
# A cada 50 interações, perde as mais antigas
# Bom para testar diferentes cenários
```

**Se quer Marcy com memória infinita:**
```python
LIMITE_HISTORICO_TOTAL = 1000
# Nunca perde histórico (até disco encher 😅)
# Máxima personalizaçãolongo termo
```

---

## 🧩 PARÂMETRO: INTERVALO_ATUALIZACAO

**Arquivo**: `marcy_pet.py` (linha ~19)

```python
INTERVALO_ATUALIZACAO = 300  # milissegundos
```

### O que faz?
Tempo entre cada atualização de frame. Menor = mais rápido.

### Ajustes por Cenário

| Valor | Velocidade | Caso de Uso | CPU |
|-------|-----------|-----------|-----|
| 200 | Muito rápido | Teste, animação fluida | 🔴 Alto |
| **300** | **Padrão suave** | **Uso normal** | **🟡 Médio** |
| 400 | Lento | Economia de bateria | 🟢 Baixo |
| 500+ | Muito lento | Máxima economia | 🟢 Muito baixo |

### Exemplos

**Se quer Marcy mais responsiva:**
```python
INTERVALO_ATUALIZACAO = 200  # 2x mais rápido
# Marcy reage mais rápido aos eventos
# CPU usa mais energia
```

**Se quer Marcy muito lenta (econômica):**
```python
INTERVALO_ATUALIZACAO = 500  # 1.6x mais lento
# Marcy se move muito devagar
# Economiza bateria
```

---

## 🧩 PARÂMETRO: VELOCIDADE_MOVIMENTO

**Arquivo**: `marcy_pet.py` (linha ~20)

```python
VELOCIDADE_MOVIMENTO = 0.8  # pixels por frame
```

### O que faz?
Quantos pixels Marcy se move a cada frame.

### Ajustes por Cenário

| Valor | Distância por frame | Efeito | Caso |
|-------|-------------------|--------|------|
| 0.3 | Muito pequeno | Movimento muito lento | Economia |
| **0.8** | **Padrão** | **Suave e natural** | **Uso normal** |
| 1.5 | Rápido | Movimento ágil | Ativo |
| 2.0 | Muito rápido | Super ágil | Debug |

### Exemplos

**Se quer Marcy morder a bola (muito ativa):**
```python
VELOCIDADE_MOVIMENTO = 1.5
# Com INTERVALO_ATUALIZACAO = 200
# Resultado: Marcy muito rápida e agitada
```

**Se quer Marcy lenta e relaxada:**
```python
VELOCIDADE_MOVIMENTO = 0.3
# Com INTERVALO_ATUALIZACAO = 400
# Resultado: Marcy muito lenta
```

---

## 🧩 PARÂMETRO: DURACAO_PARADA

**Arquivo**: `marcy_pet.py` (linha ~24)

```python
DURACAO_PARADA = (12, 24)  # segundos (min, max)
```

### O que faz?
Quanto tempo Marcy fica parada entre caminhadas.

### Ajustes por Cenário

| Valor | Parada | Modo |
|-------|--------|------|
| (6, 10) | Curta | Marcy agitada, sempre se mexendo |
| **(12, 24)** | **Padrão** | **Natural, repousada** |
| (20, 40) | Longa | Marcy contemplativa, meditativa |
| (30, 60) | Muito longa | Marcy quase estátua |

### Exemplos

**Se quer Marcy mais ativa:**
```python
DURACAO_PARADA = (6, 12)
# Descansa pouco, caminha frequente
```

**Se quer Marcy contemplativa:**
```python
DURACAO_PARADA = (25, 45)
# Descansa muito, caminha pouco
# Parece estar pensando
```

---

## 🧩 PARÂMETRO: INTERVALO_SUB_IDLE

**Arquivo**: `marcy_pet.py` (linha ~25)

```python
INTERVALO_SUB_IDLE = (6, 14)  # segundos (min, max)
```

### O que faz?
Frequência com que Marcy muda de expressão enquanto parada.

### Ajustes por Cenário

| Valor | Frequência | Efeito |
|-------|-----------|--------|
| (2, 4) | Muito alta | Marcy sempre mudando expressão |
| **(6, 14)** | **Padrão** | **Natural** |
| (15, 30) | Baixa | Marcy contemplativa |
| (30, 60) | Muito baixa | Marcy quase congelada |

### Exemplos

**Se quer Marcy expressiva e animada:**
```python
INTERVALO_SUB_IDLE = (3, 7)
# Muda expressão a cada 3-7s
```

**Se quer Marcy zen:**
```python
INTERVALO_SUB_IDLE = (20, 40)
# Muda expressão raramente
```

---

## 🧩 PARÂMETRO: CONTEXTOS_PALAVRAS

**Arquivo**: `systems/memory_rag_system.py` (linhas ~17-24)

```python
CONTEXTOS_PALAVRAS = {
    "programacao": ["código", "bug", "erro", ...],
    "pessoal": ["nome", "idade", ...],
    "trabalho": ["projeto", "reunião", ...],
    "criatividade": ["desenho", "arte", ...],
}
```

### O que faz?
Define quais palavras classificam um contexto.

### Como Adicionar Novo Contexto

```python
CONTEXTOS_PALAVRAS = {
    # ... contextos existentes ...
    
    # Novo contexto: games
    "games": ["minecraft", "fortnite", "rpg", "jogo", "controller", "pc gamer"],
    
    # Novo contexto: humor
    "humor": ["piada", "engraçado", "riso", "hilário", "cômico"],
}
```

Agora Marcy vai detectar contexto "games" automaticamente!

### Dica
Use palavras-chave específicas para melhor detecção:
- ❌ Evite: "de" "em" "para" (muito genéricas)
- ✅ Use: "código" "bug" "função" (específicas do domínio)

---

## 📊 PRESETS (Configurações Prontas)

### Preset 1: Marcy Energética 🚀
```python
INTERVALO_ATUALIZACAO = 200
VELOCIDADE_MOVIMENTO = 1.2
DURACAO_PARADA = (6, 12)
INTERVALO_SUB_IDLE = (3, 7)
LIMITE_CONTEXTO_RAG = 5
```
→ Marcy muito ativa, se move rápido, fala com menos contexto

### Preset 2: Marcy Meditativa 🧘
```python
INTERVALO_ATUALIZACAO = 400
VELOCIDADE_MOVIMENTO = 0.5
DURACAO_PARADA = (25, 45)
INTERVALO_SUB_IDLE = (20, 40)
LIMITE_CONTEXTO_RAG = 10
```
→ Marcy lenta, contemplativa, máximo contexto

### Preset 3: Marcy Balanceada ⚖️ (PADRÃO)
```python
INTERVALO_ATUALIZACAO = 300
VELOCIDADE_MOVIMENTO = 0.8
DURACAO_PARADA = (12, 24)
INTERVALO_SUB_IDLE = (6, 14)
LIMITE_CONTEXTO_RAG = 7
```
→ Marcy natural e coerente

### Preset 4: Marcy Econômica 🔋
```python
INTERVALO_ATUALIZACAO = 500
VELOCIDADE_MOVIMENTO = 0.5
DURACAO_PARADA = (30, 60)
INTERVALO_SUB_IDLE = (30, 60)
LIMITE_CONTEXTO_RAG = 3
LIMITE_HISTORICO_TOTAL = 50
```
→ Máxima economia de bateria

---

## 🎯 Checklist de Sintonia

- [ ] **Identifique o problema**: Muito rápido? Sem contexto? Esquecida?
- [ ] **Escolha o parâmetro**: INTERVALO_ATUALIZACAO? LIMITE_CONTEXTO_RAG?
- [ ] **Ajuste incrementalmente**: +10% ou -10% por vez
- [ ] **Teste por 2-3 minutos**: Observe o comportamento
- [ ] **Repita**: Se ainda não está bom, ajuste novamente
- [ ] **Documente**: Anote qual preset ficou melhor

---

## 🐛 Debugging

**Marcy se move muito rápido:**
1. ↑ Aumente `INTERVALO_ATUALIZACAO` (300 → 400)
2. ↓ Diminua `VELOCIDADE_MOVIMENTO` (0.8 → 0.5)
3. ↑ Aumente `DURACAO_PARADA` (12-24 → 16-32)

**Marcy não referencia conversas anteriores:**
1. ↑ Aumente `LIMITE_CONTEXTO_RAG` (7 → 10)
2. ↑ Aumente `LIMITE_HISTORICO_TOTAL` (200 → 300)
3. ✓ Verifique se o histórico tem itens (> 10 interações)

**Marcy responde sempre a mesma coisa:**
1. ✓ Confirme se o Ollama está rodando
2. ↑ Aumente `LIMITE_CONTEXTO_RAG` para dar mais contexto
3. → Teste com frases diferentes

---

**Última atualização**: 18 de junho de 2026  
**Versão**: 2.0
