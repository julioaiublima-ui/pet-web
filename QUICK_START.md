# 🚀 QUICK START - Mudanças v2.0

## Resumo das Correções (2 Minutos)

### ✅ Problema 1 Corrigido: Movimento Lento
- Marcy está **60% mais lenta** ✅
- Descansa **2x mais** entre movimentos ✅
- Menos fidgety, mais natural ✅

**Como**: Parâmetros otimizados em `marcy_pet.py`

### ✅ Problema 2 Corrigido: Memória com Contexto
- Histórico de **200 itens** (era 100) ✅
- **Classificação automática** por tema ✅
- **RAG** inteligente implementado ✅
- Marcy **referencia conversas anteriores** ✅

**Como**: Sistema `memory_rag_system.py` novo + integração em `marcy_ai.py`

---

## 🎯 Teste Agora

```bash
# 1. Validar tudo
python3 test_rag.py

# 2. Rodar Marcy
python3 marcy_pet.py

# 3. Converse e veja a magia! ✨
```

---

## 📚 Documentação

| Doc | Objetivo | Tempo |
|-----|----------|-------|
| [RESUMO_CORREÇÕES.md](RESUMO_CORREÇÕES.md) | Visão geral visual | 5 min |
| [CHANGELOG.md](CHANGELOG.md) | Mudanças v2.0 | 5 min |
| [MELHORIAS.md](MELHORIAS.md) | Técnico detalhado | 15 min |
| [FINE_TUNING_GUIDE.md](FINE_TUNING_GUIDE.md) | Como ajustar | 10 min |
| [test_rag.py](test_rag.py) | Exemplos práticos | Rodar |

---

## 🎛️ Ajustes Rápidos

### Marcy muito rápida? 🚀
```python
# Em marcy_pet.py, linha 19
INTERVALO_ATUALIZACAO = 400  # ↑ mais lento
```

### Marcy esquerça fácil? 🧠
```python
# Em systems/memory_rag_system.py, linha 13
LIMITE_CONTEXTO_RAG = 10  # ↑ mais contexto
```

### Marcy muito contemplativa? 🧘
```python
# Em marcy_pet.py
INTERVALO_ATUALIZACAO = 500
DURACAO_PARADA = (30, 60)
```

Veja [FINE_TUNING_GUIDE.md](FINE_TUNING_GUIDE.md) para todos os presets!

---

## ✨ O que Mudou

### Arquivos Novos
- `systems/memory_rag_system.py` - RAG completo
- `config.json` - Configuração
- `test_rag.py` - Testes
- `MELHORIAS.md` - Docs
- `RESUMO_CORREÇÕES.md` - Resumo
- `FINE_TUNING_GUIDE.md` - Guia
- `CHANGELOG.md` - Histórico

### Arquivos Modificados
- `marcy_pet.py` - Parâmetros otimizados
- `marcy_ai.py` - RAG integrado
- `systems/memory_system.py` - Wrapper RAG

---

## 🚨 Se Algo Deu Errado

### Erro de import?
```bash
python3 test_rag.py  # Deve passar todos os testes
```

### Marcy não responde?
```bash
# Verifique se Ollama está rodando
# Se não: brew install ollama && ollama serve
```

### Marcy muito burra?
Aumentar contexto:
```python
LIMITE_CONTEXTO_RAG = 10  # em memory_rag_system.py
```

---

## 📊 Números

| Métrica | Antes | Depois | Ganho |
|---------|-------|--------|-------|
| Velocidade | 2px/frame | 0.8px/frame | 60% mais lento |
| Intervalo | 150ms | 300ms | 2x mais suave |
| Parada | 6-14s | 12-24s | 2x mais descanso |
| Histórico | 100 | 200 | 2x maior |
| Contexto | 0 | 4 temas | ∞ |

---

## ✅ Checklist

- [ ] Li este arquivo (2 min)
- [ ] Rodei `test_rag.py` (passou ✅)
- [ ] Testei movimento (mais lento ✅)
- [ ] Testei memória (com contexto ✅)
- [ ] Personalizei parâmetros (opcional)
- [ ] Consultei FINE_TUNING_GUIDE.md (se customizou)

---

## 🎉 Tá pronto!

```
python3 marcy_pet.py
```

Marcy Pet v2.0 com:
✅ Movimento natural
✅ Memória inteligente (RAG)
✅ Contexto automático
✅ Totalmente ajustável

**Divirta-se!** 🚀

---

_Documentação completa em: [MELHORIAS.md](MELHORIAS.md)_
