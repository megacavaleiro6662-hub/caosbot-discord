#!/usr/bin/env python3
# Script para remover tentativa de gerar imagem e deixar só embed perfeito

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover função de criar imagem
old_function = """# ========================================
# FUNÇÃO PARA GERAR IMAGEM DE SHIP COM API EXTERNA
# ========================================

async def create_ship_image(user1, user2, ship_value, ship_name):
    \"\"\"Cria imagem de ship usando API externa some-random-api.com\"\"\"
    try:
        # URL da API com avatares dos usuários
        avatar1_url = str(user1.display_avatar.url)
        avatar2_url = str(user2.display_avatar.url)
        
        # API some-random-api.com para gerar ship
        api_url = f"https://some-random-api.com/canvas/misc/ship?user1={avatar1_url}&user2={avatar2_url}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return BytesIO(image_data)
                else:
                    print(f"❌ Erro na API: Status {resp.status}")
                    return None
    
    except Exception as e:
        print(f"❌ Erro ao gerar imagem de ship: {e}")
        return None

"""

content = content.replace(old_function, "")

# Remover tentativa de gerar imagem no comando ship
old_ship_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Gerar imagem de ship
    ship_image = await create_ship_image(user1, user2, ship_value, ship_name)
    
    if ship_image:
        # Enviar com imagem
        file = discord.File(ship_image, filename='ship.png')
        embed.set_image(url='attachment://ship.png')
        await ctx.reply(embed=embed, file=file)
    else:
        # Se falhar, envia sem imagem
        await ctx.reply(embed=embed)"""

new_ship_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Enviar embed (sem imagem)
    await ctx.reply(embed=embed)"""

content = content.replace(old_ship_end, new_ship_end)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comando ship simplificado - so embed perfeito!")
