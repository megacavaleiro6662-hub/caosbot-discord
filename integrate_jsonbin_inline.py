# -*- coding: utf-8 -*-
# Integrar JSONBin inline (sem arquivo separado)

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover import do jsonbin_config
content = content.replace('from jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin\n', '')

# Código JSONBin inline
jsonbin_inline = '''
# ========================================
# JSONBIN.IO - PERSISTENCIA DE CONFIGURACOES
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
                print(f"[JSONBIN] Bin criado! ADICIONE NO RENDER: JSONBIN_BIN_ID={JSONBIN_BIN_ID}")
        if response.status_code in [200, 201]:
            print(f"[JSONBIN] Config salva!")
            return True
        return False
    except Exception as e:
        print(f"[JSONBIN] Erro ao salvar: {e}")
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
target = '# Arquivo de configuração (NÃO USADO NO RENDER - apenas backup local)'
if target in content and 'JSONBIN_API_KEY' not in content:
    content = content.replace(target, jsonbin_inline + target)
    print("[OK] JSONBin integrado inline")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCESSO] JSONBin agora esta inline no arquivo principal!")
