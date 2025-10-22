# -*- coding: utf-8 -*-
# Fix: Mover import jsonbin_config para o topo

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover import do final
content = content.replace('\nfrom jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin\n', '\n')

# Adicionar no topo, após 'from http.server import'
import_line = 'from jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin'

# Encontrar posição após 'from http.server import'
pos = content.find('from http.server import HTTPServer, BaseHTTPRequestHandler')
if pos != -1:
    # Encontrar fim da linha
    end_pos = content.find('\n', pos)
    if end_pos != -1:
        # Inserir após essa linha
        content = content[:end_pos+1] + import_line + '\n' + content[end_pos+1:]
        print("[OK] Import movido para o topo!")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCESSO] Import corrigido!")
