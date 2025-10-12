#!/usr/bin/env python3
# Script para atualizar bot para usar servidor de imagens

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar variável de ambiente para URL do servidor de imagens no início
env_var = """
# URL do servidor de imagens (notebook)
IMAGE_SERVER_URL = os.getenv('IMAGE_SERVER_URL', '')  # Deixa vazio se não tiver

"""

# Encontrar onde inserir (depois dos imports, antes das primeiras variáveis)
insert_pos = content.find("# Configurações do bot")
if insert_pos == -1:
    insert_pos = content.find("DISCORD_TOKEN = os.getenv")
    
if insert_pos != -1:
    content = content[:insert_pos] + env_var + content[insert_pos:]

# Atualizar função de criar imagem para chamar o servidor
old_function = """async def create_ship_image_local(user1, user2, ship_value, ship_name):
    \"\"\"Gera imagem de ship usando Pillow (só funciona no notebook)\"\"\"
    try:"""

new_function = """async def create_ship_image_local(user1, user2, ship_value, ship_name):
    \"\"\"Gera imagem de ship usando servidor externo ou Pillow local\"\"\"
    
    # Tentar usar servidor externo primeiro (notebook)
    if IMAGE_SERVER_URL:
        try:
            avatar1 = str(user1.display_avatar.url)
            avatar2 = str(user2.display_avatar.url)
            
            url = f"{IMAGE_SERVER_URL}/ship?avatar1={avatar1}&avatar2={avatar2}&percentage={ship_value}&name={ship_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        print(f"✅ Imagem gerada pelo servidor externo!")
                        return BytesIO(image_data)
                    else:
                        print(f"⚠️ Servidor retornou {resp.status}, tentando Pillow local...")
        except Exception as e:
            print(f"⚠️ Erro ao chamar servidor: {e}, tentando Pillow local...")
    
    # Fallback: tentar Pillow local
    try:"""

content = content.replace(old_function, new_function)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Bot atualizado para usar servidor de imagens!")
