#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script para adicionar o comando .scan no caosbot_railway.py

# Ler o arquivo principal
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ler o comando scan
with open('comando_scan.py', 'r', encoding='utf-8') as f:
    scan_code = f.read()

# Remover o cabeçalho do comando_scan.py
scan_code = scan_code.replace(
    '# ========================================\n'
    '# COMANDO .SCAN - ADICIONAR NO caosbot_railway.py\n'
    '# ========================================\n'
    '# COPIE TODO ESTE CÓDIGO E COLE APÓS O @restart_command.error\n'
    '# (Linha 2453, antes do "# SISTEMA ANTI-SPAM")\n\n', 
    ''
)

# Adicionar o comando antes da seção de anti-spam
marker = '# ========================================\n# SISTEMA ANTI-SPAM - VERSÃO FINAL\n# ========================================'

if marker in content:
    new_content = content.replace(
        marker,
        '\n# ========================================\n'
        '# COMANDO .SCAN - PEGAR TODOS OS IDS DO SERVIDOR\n'
        '# ========================================\n'
        + scan_code + '\n\n'
        + marker
    )
    
    # Salvar
    with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('OK - Comando .scan adicionado com sucesso!')
else:
    print('ERRO - Marcador nao encontrado!')
