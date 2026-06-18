#!/usr/bin/env python3
"""Validação final das mudanças implementadas"""

import json
from pathlib import Path
import sys

def check_file_exists(path, description):
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} NÃO ENCONTRADO: {path}")
        return False

def check_python_syntax(path):
    try:
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
        return True
    except SyntaxError as e:
        print(f"  ⚠️  Erro de sintaxe: {e}")
        return False

def check_imports():
    try:
        from systems.memory_rag_system import (
            detectar_contexto,
            recuperar_contexto_rag,
            montar_contexto_rag,
        )
        from systems.memory_system import carregar_memoria
        from marcy_ai import responder
        print("✅ Todos os imports funcionam")
        return True
    except Exception as e:
        print(f"❌ Erro de import: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  VALIDAÇÃO FINAL DAS MUDANÇAS - MARCY PET")
    print("="*60 + "\n")
    
    files_ok = True
    
    print("📁 Verificando Arquivos:\n")
    files_ok &= check_file_exists("systems/memory_rag_system.py", "Sistema RAG")
    files_ok &= check_file_exists("marcy_pet.py", "Marcy Pet (modificado)")
    files_ok &= check_file_exists("marcy_ai.py", "Marcy AI (modificado)")
    files_ok &= check_file_exists("systems/memory_system.py", "Memory System (modificado)")
    files_ok &= check_file_exists("config.json", "Arquivo de configuração")
    files_ok &= check_file_exists("MELHORIAS.md", "Documentação de melhorias")
    files_ok &= check_file_exists("RESUMO_CORREÇÕES.md", "Resumo das correções")
    files_ok &= check_file_exists("FINE_TUNING_GUIDE.md", "Guia de fine-tuning")
    
    print("\n🐍 Verificando Sintaxe Python:\n")
    python_files = [
        "marcy_pet.py",
        "marcy_ai.py", 
        "systems/memory_system.py",
        "systems/memory_rag_system.py"
    ]
    
    for f in python_files:
        path = Path(f)
        if path.exists():
            if check_python_syntax(str(path)):
                print(f"✅ Sintaxe OK: {f}")
            else:
                files_ok = False
    
    print("\n🔗 Verificando Imports:\n")
    files_ok &= check_imports()
    
    print("\n📋 Verificando Parâmetros Otimizados:\n")
    try:
        with open("marcy_pet.py", "r") as f:
            content = f.read()
            checks = [
                ("INTERVALO_ATUALIZACAO = 300", "Intervalo otimizado para 300ms"),
                ("VELOCIDADE_MOVIMENTO = 0.8", "Velocidade otimizada para 0.8px"),
                ("DURACAO_PARADA = (12, 24)", "Parada otimizada para 12-24s"),
                ("INTERVALO_SUB_IDLE = (6, 14)", "Sub-idle otimizado para 6-14s"),
            ]
            
            for param, desc in checks:
                if param in content:
                    print(f"✅ {desc}")
                else:
                    print(f"❌ {desc} NÃO ENCONTRADO")
                    files_ok = False
    except Exception as e:
        print(f"❌ Erro ao verificar parâmetros: {e}")
        files_ok = False
    
    print("\n🧠 Verificando Sistema RAG:\n")
    try:
        with open("systems/memory_rag_system.py", "r") as f:
            content = f.read()
            checks = [
                ("LIMITE_CONTEXTO_RAG = 10", "Limite de contexto RAG"),
                ("LIMITE_HISTORICO_TOTAL = 200", "Limite de histórico total"),
                ("detectar_contexto", "Função de detecção de contexto"),
                ("recuperar_contexto_rag", "Função de recuperação RAG"),
                ("CONTEXTOS_PALAVRAS", "Dicionário de contextos"),
            ]
            
            for param, desc in checks:
                if param in content:
                    print(f"✅ {desc}")
                else:
                    print(f"❌ {desc} NÃO ENCONTRADO")
                    files_ok = False
    except Exception as e:
        print(f"❌ Erro ao verificar RAG: {e}")
        files_ok = False
    
    print("\n📊 Resumo da Validação:\n")
    if files_ok:
        print("=" * 60)
        print("  ✅ TODAS AS VALIDAÇÕES PASSARAM!")
        print("  Sistema pronto para uso")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("  ⚠️  ALGUMAS VALIDAÇÕES FALHARAM")
        print("  Verifique os erros acima")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
