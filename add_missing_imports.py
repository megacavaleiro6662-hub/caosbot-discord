# -*- coding: utf-8 -*-
# Adicionar imports faltantes

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de imports necessários
imports_to_add = []

if 'from collections import' not in content:
    imports_to_add.append('from collections import defaultdict, deque')
    print("[ADD] from collections import defaultdict, deque")

if 'from threading import Thread' not in content:
    imports_to_add.append('from threading import Thread')
    print("[ADD] from threading import Thread")

if 'from http.server import' not in content:
    imports_to_add.append('from http.server import HTTPServer, BaseHTTPRequestHandler')
    print("[ADD] from http.server import HTTPServer, BaseHTTPRequestHandler")

if imports_to_add:
    # Adicionar após a linha 'from jsonbin_config import...'
    target = 'from jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin'
    if target in content:
        new_imports = '\n'.join(imports_to_add)
        content = content.replace(target, target + '\n' + new_imports)
        print(f"\n[OK] {len(imports_to_add)} imports adicionados!")
    
    with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[SUCESSO] Imports corrigidos!")
else:
    print("[INFO] Todos os imports já estão presentes!")
