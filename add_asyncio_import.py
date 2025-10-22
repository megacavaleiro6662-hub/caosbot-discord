# -*- coding: utf-8 -*-
# Adicionar import asyncio

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Adicionar após 'import requests'
new_lines = []
import_added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    if line.strip() == 'import requests' and not import_added:
        # Verificar se asyncio já não está na próxima linha
        if i+1 < len(lines) and 'import asyncio' not in lines[i+1]:
            new_lines.append('import asyncio\n')
            import_added = True
            print("[OK] Adicionado: import asyncio")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[SUCESSO] Import asyncio adicionado!")
