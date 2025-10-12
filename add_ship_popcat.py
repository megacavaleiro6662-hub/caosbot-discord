#!/usr/bin/env python3
# Script para adicionar API do PopCat que funciona melhor

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar função de gerar imagem com PopCat API (antes do @bot.command(name='ship'))
ship_function = """# ========================================
# FUNÇÃO PARA GERAR IMAGEM DE SHIP
# ========================================

async def create_ship_image(user1, user2):
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
        return None

"""

# Encontrar onde inserir
insert_pos = content.find("@bot.command(name='ship')")
if insert_pos != -1:
    content = content[:insert_pos] + ship_function + content[insert_pos:]

# Atualizar final do comando para usar a imagem
old_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Enviar embed (sem imagem)
    await ctx.reply(embed=embed)"""

new_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Tentar gerar imagem
    ship_image = await create_ship_image(user1, user2)
    
    if ship_image:
        file = discord.File(ship_image, filename='ship.png')
        embed.set_image(url='attachment://ship.png')
        await ctx.reply(embed=embed, file=file)
    else:
        # Se falhar, envia só o embed
        await ctx.reply(embed=embed)"""

content = content.replace(old_end, new_end)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("API PopCat adicionada para gerar imagem!")
