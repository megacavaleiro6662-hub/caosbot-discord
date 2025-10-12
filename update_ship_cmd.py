#!/usr/bin/env python3
# Script para atualizar comando ship para usar imagem

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar o final do comando ship e adicionar geração de imagem
old_ship_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

new_ship_end = """    embed.set_footer(
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

content = content.replace(old_ship_end, new_ship_end)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comando ship atualizado para usar imagem!")
