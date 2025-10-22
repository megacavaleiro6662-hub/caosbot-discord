# -*- coding: utf-8 -*-
# Fix: Adicionar import jsonbin_config no topo

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar linha com 'import requests' e adicionar depois
new_lines = []
import_added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    if line.strip() == 'import requests' and not import_added:
        new_lines.append('from jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin\n')
        import_added = True
        print("[OK] Import adicionado apos 'import requests'")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[SUCESSO] Import corrigido!")
