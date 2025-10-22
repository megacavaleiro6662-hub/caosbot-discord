#!/usr/bin/env python3
# Script para integrar JSONBin ao caosbot_railway.py

import re

# Ler o arquivo
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Código para adicionar DEPOIS de 'import os'
jsonbin_code = '''import requests'''

# Adicionar import requests se não existir
if 'import requests' not in content:
    content = content.replace('import os', 'import os\nimport requests')
    print("[OK] Adicionado: import requests")

# Código JSONBin para adicionar
jsonbin_system = '''
# ========================================
# 🌐 JSONBIN.IO - SISTEMA DE PERSISTÊNCIA
# ========================================
JSONBIN_API_KEY = "$2a$10$OLp47wzSpJZqq7gAVgUgkO4qJQa6pAk6oL0pZ0OrV/Z.7HwQ/TRrq"
JSONBIN_BIN_ID = os.getenv('JSONBIN_BIN_ID', None)
JSONBIN_API_URL = "https://api.jsonbin.io/v3/b"

def save_config_to_jsonbin(config_data):
    """Salva configuracoes no JSONBin"""
    global JSONBIN_BIN_ID
    try:
        headers = {'Content-Type': 'application/json', 'X-Master-Key': JSONBIN_API_KEY}
        
        if JSONBIN_BIN_ID:
            response = requests.put(f"{JSONBIN_API_URL}/{JSONBIN_BIN_ID}", json=config_data, headers=headers)
        else:
            response = requests.post(JSONBIN_API_URL, json=config_data, headers=headers)
            if response.status_code == 200:
                JSONBIN_BIN_ID = response.json()['metadata']['id']
                print(f"[OK] Bin criado! ADICIONE NO RENDER: JSONBIN_BIN_ID={JSONBIN_BIN_ID}")
        
        if response.status_code in [200, 201]:
            print(f"[OK] Config salva no JSONBin!")
            return True
        return False
    except Exception as e:
        print(f"[ERRO] Erro JSONBin: {e}")
        return False

def load_config_from_jsonbin():
    """Carrega configuracoes do JSONBin"""
    if not JSONBIN_BIN_ID:
        return None
    try:
        headers = {'X-Master-Key': JSONBIN_API_KEY}
        response = requests.get(f"{JSONBIN_API_URL}/{JSONBIN_BIN_ID}/latest", headers=headers)
        if response.status_code == 200:
            return response.json()['record']
        return None
    except:
        return None

'''

# Adicionar antes de "# Arquivo de configuração"
if '# 🌐 JSONBIN.IO - SISTEMA DE PERSISTÊNCIA' not in content:
    content = content.replace(
        '# Arquivo de configuração (NÃO USADO NO RENDER - apenas backup local)',
        jsonbin_system + '# Arquivo de configuração (backup local)'
    )
    print("[OK] Adicionado: Sistema JSONBin")

# Modificar welcome_config para carregar do JSONBin
old_welcome_config = '''# Estado do sistema (DESATIVADO por padrão - aguarda dashboard)
welcome_config = {
    'welcome_enabled': False,  # ❌ Aguardando dashboard
    'goodbye_enabled': False,  # ❌ Aguardando dashboard
    'tickets_enabled': False,  # ❌ Aguardando dashboard
    'status_message_id': None
}'''

new_welcome_config = '''# Estado do sistema - CARREGA DO JSONBIN
print("[INFO] Tentando carregar do JSONBin...")
welcome_config = load_config_from_jsonbin() or {
    'welcome_enabled': False,
    'goodbye_enabled': False,
    'autorole_enabled': False,
    'tickets_enabled': False,
    'status_message_id': None
}'''
}
print(f"[OK] Config: welcome={welcome_config.get('welcome_enabled')}, goodbye={welcome_config.get('goodbye_enabled')}")'''

if old_welcome_config in content:
    content = content.replace(old_welcome_config, new_welcome_config)
    print("[OK] Modificado: welcome_config para carregar do JSONBin")

# Modificar save_welcome_config para salvar no JSONBin
old_save = '''def save_welcome_config():
    """Salva configurações do sistema de boas-vindas"""
    try:
        with open(WELCOME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(welcome_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configurações de boas-vindas salvas")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações de boas-vindas: {e}")'''

new_save = '''def save_welcome_config():
    """Salva configurações (JSONBin + backup local)"""
    try:
        # Salvar no JSONBin (persistente)
        save_config_to_jsonbin(welcome_config)
        
        # Backup local
        with open(WELCOME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(welcome_config, f, indent=2, ensure_ascii=False)
        print(f"[OK] Configuracoes salvas (JSONBin + local)")
    except Exception as e:
        print(f"[ERRO] Erro ao salvar: {e}")'''

if old_save in content:
    content = content.replace(old_save, new_save)
    print("[OK] Modificado: save_welcome_config para usar JSONBin")

# Salvar arquivo modificado
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCESSO] INTEGRACAO JSONBIN COMPLETA!")
print("[INFO] Proximos passos:")
print("   1. Commit e push das mudanças")
print("   2. Após primeiro deploy, pegue o JSONBIN_BIN_ID do log")
print("   3. Adicione JSONBIN_BIN_ID nas variáveis de ambiente do Render")
