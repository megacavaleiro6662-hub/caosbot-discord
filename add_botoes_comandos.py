#!/usr/bin/env python3
# Script para adicionar botões aos comandos

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== BEIJAR COM BOTÃO ====================
old_beijar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='abracar')"""

new_beijar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'kiss', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='abracar')"""

content = content.replace(old_beijar_final, new_beijar_final)

# ==================== ABRAÇAR COM BOTÃO ====================
old_abracar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='acariciar')"""

new_abracar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'hug', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='acariciar')"""

content = content.replace(old_abracar_final, new_abracar_final)

# ==================== ACARICIAR COM BOTÃO ====================
old_acariciar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='tapa')"""

new_acariciar_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'pat', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='tapa')"""

content = content.replace(old_acariciar_final, new_acariciar_final)

# ==================== CAFUNÉ COM BOTÃO ====================
old_cafune_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

# ========================================
# COMANDOS DE CONTROLE - BOAS-VINDAS/SAÍDA/BAN"""

new_cafune_final = """    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'pat', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

# ========================================
# COMANDOS DE CONTROLE - BOAS-VINDAS/SAÍDA/BAN"""

content = content.replace(old_cafune_final, new_cafune_final)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Botoes adicionados aos comandos beijar, abracar, acariciar e cafune!")
