# -*- coding: utf-8 -*-
# Fix: Adicionar import collections

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Adicionar após 'import requests'
new_lines = []
import_added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    if 'from jsonbin_config import' in line and not import_added:
        new_lines.append('from collections import defaultdict, deque\n')
        new_lines.append('from threading import Thread\n')
        new_lines.append('from http.server import HTTPServer, BaseHTTPRequestHandler\n')
        import_added = True
        print("[OK] Imports faltantes adicionados")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[SUCESSO] Todos imports corrigidos!")
