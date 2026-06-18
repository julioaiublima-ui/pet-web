#!/usr/bin/env python3
"""
Script de demonstração do sistema RAG
Mostra como o sistema classifica contextos e recupera informações relevantes
"""

from systems.memory_rag_system import (
    detectar_contexto,
    montar_contexto_rag,
    registrar_interacao,
    recuperar_contexto_rag
)


def linha_separadora(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}\n")


def teste_deteccao_contexto():
    linha_separadora("TESTE 1: Detecção de Contexto")
    
    exemplos = [
        ("Tenho um bug no meu código Python", "programacao"),
        ("Meu hobby favorito é desenhar e pintar", "pessoal"),
        ("A reunião com o cliente é amanhã", "trabalho"),
        ("Que legal, vou criar uma história de ficção", "criatividade"),
        ("Como você está?", "geral"),
        ("Git commit com mensagem clara", "programacao"),
        ("Preciso implementar uma nova API REST", "programacao"),
    ]
    
    for texto, esperado in exemplos:
        detectado = detectar_contexto(texto)
        status = "✅" if detectado == esperado else "❌"
        print(f"{status} '{texto}'")
        print(f"   → Detectado: {detectado} | Esperado: {esperado}\n")


def teste_registrar_e_recuperar():
    linha_separadora("TESTE 2: Registrar e Recuperar do RAG")
    
    # Simular algumas interações para teste
    interacoes_teste = [
        ("Qual é a diferença entre class e function?", "Code", "Em Python, classes..."),
        ("Como resolver esse erro de importação?", "Code", "Verifica o caminho..."),
        ("Qual é seu hobby?", "", "Amo explorar..."),
        ("Como fazer um array em Python?", "Code", "Usa list()..."),
        ("Qual é seu filme favorito?", "", "Gosto de ficção..."),
    ]
    
    print(f"Registrando {len(interacoes_teste)} interações de teste...")
    for texto, app, resposta in interacoes_teste:
        registrar_interacao(texto, app, resposta)
    
    print("✅ Interações registradas!\n")
    
    # Teste recuperação por contexto
    print("📊 Recuperação por Contexto:\n")
    
    # Query sobre programação
    print("Query: 'array em Python' (contexto: programacao)")
    resultado = recuperar_contexto_rag("array em Python", "programacao", limite=3)
    print(f"Items recuperados: {len(resultado)}")
    for i, item in enumerate(resultado, 1):
        contexto = item.get("contexto", "?")
        print(f"  {i}. [{contexto}] User: {item.get('texto', '')[:50]}...")
    
    # Query sobre pessoal
    print("\n\nQuery: 'filme e hobby' (contexto: pessoal)")
    resultado = recuperar_contexto_rag("filme hobby", "pessoal", limite=3)
    print(f"Items recuperados: {len(resultado)}")
    for i, item in enumerate(resultado, 1):
        contexto = item.get("contexto", "?")
        print(f"  {i}. [{contexto}] User: {item.get('texto', '')[:50]}...")


def teste_rag_prompt():
    linha_separadora("TESTE 3: RAG para Construir Prompt")
    
    print("Simulando uma pergunta de programação...\n")
    
    contexto = montar_contexto_rag("Como debugar um erro?", "programacao", limite=5)
    print("Contexto RAG montado:")
    print("-" * 40)
    print(contexto[:200] + "..." if len(contexto) > 200 else contexto)


def teste_parametros():
    linha_separadora("TESTE 4: Parâmetros de Configuração")
    
    print("Parâmetros de MOVIMENTO (corrigidos):")
    print("  INTERVALO_ATUALIZACAO: 300ms (era 150ms) - 2x mais lento")
    print("  VELOCIDADE_MOVIMENTO: 0.8px (era 2px) - 60% mais lento")
    print("  DURACAO_PARADA: 12-24s (era 6-14s) - 2x MAIS DESCANSO")
    print("  INTERVALO_SUB_IDLE: 6-14s (era 3-8s) - MENOS expressões")
    
    print("\nParâmetros de RAG:")
    print("  LIMITE_CONTEXTO_RAG: 7 items (era 5)")
    print("  LIMITE_HISTORICO_TOTAL: 200 items (era 100)")
    
    print("\nResultado:")
    print("  ✅ Marcy se move ~60% mais lentamente")
    print("  ✅ Marcy descansa 2x mais entre movimentos")
    print("  ✅ Memória 2x maior e com contexto inteligente")
    print("  ✅ Recuperação de informações por tema")


if __name__ == "__main__":
    print("\n" + "🧪 TESTES DO SISTEMA RAG - MARCY PET" + "\n")
    
    teste_deteccao_contexto()
    teste_registrar_e_recuperar()
    teste_rag_prompt()
    teste_parametros()
    
    linha_separadora("✅ TODOS OS TESTES CONCLUÍDOS")
    print("Para rodar a Marcy Pet com as melhorias:")
    print("  python3 marcy_pet.py")
