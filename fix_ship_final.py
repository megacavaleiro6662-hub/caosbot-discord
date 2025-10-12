#!/usr/bin/env python3
# Script para usar API que funciona com IDs em vez de URLs

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir função
old_function = """async def create_ship_image(user1, user2):
    \"\"\"Gera imagem de ship usando PopCat API\"\"\"
    try:
        # URLs dos avatares
        avatar1 = str(user1.display_avatar.url)
        avatar2 = str(user2.display_avatar.url)
        
        # API PopCat (funciona melhor)
        api_url = f"https://api.popcat.xyz/ship?user1={avatar1}&user2={avatar2}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return BytesIO(image_data)
                else:
                    print(f"❌ API retornou status: {resp.status}")
                    return None
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        return None"""

new_function = """async def create_ship_image(user1, user2):
    \"\"\"Gera imagem de ship usando API Jeyy\"\"\"
    try:
        # Pegar IDs dos avatares (mais confiável)
        avatar1_id = user1.display_avatar.key
        avatar2_id = user2.display_avatar.key
        
        # Construir URLs dos avatares
        avatar1_url = f"https://cdn.discordapp.com/avatars/{user1.id}/{avatar1_id}.png"
        avatar2_url = f"https://cdn.discordapp.com/avatars/{user2.id}/{avatar2_id}.png"
        
        # API Jeyy (mais estável)
        api_url = f"https://api.jeyy.xyz/v2/image/ship?image_one={avatar1_url}&image_two={avatar2_url}"
        
        print(f"🔍 Tentando gerar ship: {api_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                print(f"📊 Status da API: {resp.status}")
                if resp.status == 200:
                    image_data = await resp.read()
                    print(f"✅ Imagem gerada: {len(image_data)} bytes")
                    return BytesIO(image_data)
                else:
                    print(f"❌ API retornou status: {resp.status}")
                    response_text = await resp.text()
                    print(f"❌ Resposta: {response_text}")
                    return None
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        import traceback
        traceback.print_exc()
        return None"""

content = content.replace(old_function, new_function)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("API trocada para Jeyy com logs detalhados!")
