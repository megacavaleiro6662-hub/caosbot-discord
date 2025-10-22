# -*- coding: utf-8 -*-
# Script simples para adicionar JSONBin ao caosbot

# Ler arquivo
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar linha com 'import os'
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if line.strip() == 'import os':
        # Adicionar import requests
        if i+1 < len(lines) and 'import requests' not in lines[i+1]:
            new_lines.append('import requests\n')
            print("[OK] Adicionado import requests")

# Escrever de volta
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[SUCESSO] Modificacao concluida!")
print("\nProximos passos:")
print("1. Vou fazer mais modificacoes para integrar JSONBin")
print("2. Commit e push")
print("3. Deploy no Render")
