# -*- coding: utf-8 -*-
import sys

# Ler arquivo
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar import no topo
if 'from jsonbin_config import' not in content:
    # Encontrar a primeira ocorrência de 'import discord'
    import_pos = content.find('import discord')
    if import_pos != -1:
        # Adicionar após os imports principais
        insert_pos = content.find('\n', content.find('from http.server import'))
        if insert_pos != -1:
            content = content[:insert_pos+1] + 'from jsonbin_config import save_config_to_jsonbin, load_config_from_jsonbin\n' + content[insert_pos+1:]
            print("[OK] Adicionado import jsonbin_config")

# 2. Modificar save_welcome_config
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
        print(f"✅ Configurações salvas (JSONBin + local)")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")'''

if old_save in content:
    content = content.replace(old_save, new_save)
    print("[OK] Modificado save_welcome_config")

# 3. Adicionar carregamento do JSONBin na inicialização
load_code = '''
# Tentar carregar configurações do JSONBin ao iniciar
print("🔄 Tentando carregar do JSONBin...")
loaded_config = load_config_from_jsonbin()
if loaded_config:
    welcome_config.update(loaded_config)
    print(f"✅ Config carregada: welcome={welcome_config.get('welcome_enabled')}, goodbye={welcome_config.get('goodbye_enabled')}")
'''

# Procurar onde adicionar (após a definição de welcome_config)
search_pattern = '''welcome_config = {
    'welcome_enabled': False,  # ❌ Aguardando dashboard
    'goodbye_enabled': False,  # ❌ Aguardando dashboard
    'autorole_enabled': False,  # ❌ Aguardando dashboard
    'tickets_enabled': False,  # ❌ Aguardando dashboard
    'status_message_id': None
}'''

if search_pattern in content and load_code not in content:
    content = content.replace(search_pattern, search_pattern + load_code)
    print("[OK] Adicionado carregamento JSONBin")

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCESSO] JSONBin integrado!")
print("\nProximos passos:")
print("1. git add .")
print("2. git commit -m 'Integrado JSONBin para persistencia'")
print("3. git push")
print("4. Apos primeiro deploy, pegue o JSONBIN_BIN_ID do log")
print("5. Adicione JSONBIN_BIN_ID nas variaveis de ambiente do Render")
