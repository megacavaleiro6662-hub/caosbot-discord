#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script para remover o comando .scan duplicado

# Ler o arquivo
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e remover a segunda ocorrência do comando scan
in_second_scan = False
start_line = None
end_line = None
scan_count = 0

for i, line in enumerate(lines):
    if "@bot.command(name='scan')" in line:
        scan_count += 1
        if scan_count == 2:
            start_line = i - 3  # Incluir o cabeçalho
            
    if start_line is not None and in_second_scan == False:
        in_second_scan = True
    
    if in_second_scan and "@scan_server.error" in line:
        # Encontrar o fim dessa seção (até a próxima linha vazia dupla ou próxima seção)
        for j in range(i, min(i + 10, len(lines))):
            if lines[j].strip() == '' and j + 1 < len(lines) and lines[j+1].strip() == '':
                end_line = j + 1
                break
            if "# ========================================" in lines[j] and j > i + 2:
                end_line = j - 1
                break
        break

if start_line is not None and end_line is not None:
    # Remover as linhas duplicadas
    new_lines = lines[:start_line] + lines[end_line:]
    
    # Salvar
    with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f'OK - Removida duplicata do comando .scan (linhas {start_line+1} a {end_line})')
else:
    print('ERRO - Nao encontrei a duplicata')
