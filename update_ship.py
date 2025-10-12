#!/usr/bin/env python3
# Script para atualizar comando ship

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== SHIP ====================
old_ship = """@bot.command(name='ship')
async def ship_command(ctx, user1: discord.Member = None, user2: discord.Member = None):
    if not user1 or not user2:
        await ctx.reply('❌ Você precisa mencionar 2 pessoas! Exemplo: `.ship @user1 @user2`')
        return
    
    # Calcula porcentagem de ship (baseado em IDs para ser consistente)
    ship_value = (user1.id + user2.id) % 101
    
    # Nome do ship (junção dos nomes)
    name1 = user1.display_name[:len(user1.display_name)//2]
    name2 = user2.display_name[len(user2.display_name)//2:]
    ship_name = f"{name1}{name2}"
    
    # Barra de progresso
    filled = '❤️' * (ship_value // 10)
    empty = '🖤' * (10 - ship_value // 10)
    bar = filled + empty
    
    # Mensagem baseada na porcentagem
    if ship_value >= 80:
        message = "💕 Perfeito! Casal do ano!"
    elif ship_value >= 60:
        message = "💖 Muito compatíveis!"
    elif ship_value >= 40:
        message = "💛 Pode dar certo!"
    elif ship_value >= 20:
        message = "💙 Quem sabe..."
    else:
        message = "💔 Melhor não..."
    
    embed = discord.Embed(
        title=f'💘 SHIPAGEM: {ship_name.upper()}',
        description=f'{user1.mention} + {user2.mention}',
        color=0xff1493
    )
    embed.add_field(name='Compatibilidade', value=f'{bar}\\n**{ship_value}%**', inline=False)
    embed.add_field(name='Resultado', value=message, inline=False)
    embed.set_footer(text=f'Ship by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_ship = """@bot.command(name='ship')
async def ship_command(ctx, user1: discord.Member = None, user2: discord.Member = None):
    if not user1 or not user2:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar 2 pessoas!\\n\\n**Exemplo:**\\n`.ship @user1 @user2`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if user1.bot or user2.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Não dá pra shipar bots!\\n*Eles não têm sentimentos românticos!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if user1.id == user2.id:
        embed = discord.Embed(
            title='😅 Narcisismo Detected',
            description=f'**{user1.mention}** não pode ser shipado consigo mesmo!\\n*Mas o amor próprio é importante!* ❤️',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    # Calcula porcentagem de ship (baseado em IDs para ser consistente)
    ship_value = (user1.id + user2.id) % 101
    
    # Nome do ship (junção dos nomes)
    name1 = user1.display_name[:len(user1.display_name)//2]
    name2 = user2.display_name[len(user2.display_name)//2:]
    ship_name = f"{name1}{name2}"
    
    # Barra de progresso visual
    filled = '❤️' * (ship_value // 10)
    empty = '🖤' * (10 - ship_value // 10)
    bar = filled + empty
    
    # Mensagem baseada na porcentagem com mais variedade
    if ship_value >= 90:
        emoji = "💕"
        message = "PERFEIÇÃO ABSOLUTA! Casal do ano! Casem logo!"
        cor = 0xff1493  # Pink forte
    elif ship_value >= 75:
        emoji = "💖"
        message = "Extremamente compatíveis! Isso vai dar certo!"
        cor = 0xff69b4  # Pink médio
    elif ship_value >= 60:
        emoji = "💗"
        message = "Muito compatíveis! Vale a pena tentar!"
        cor = 0xffc0cb  # Pink claro
    elif ship_value >= 45:
        emoji = "💛"
        message = "Pode dar certo! Precisam se conhecer melhor!"
        cor = 0xffd700  # Dourado
    elif ship_value >= 30:
        emoji = "💙"
        message = "Quem sabe com um pouco de esforço..."
        cor = 0x87ceeb  # Azul claro
    elif ship_value >= 15:
        emoji = "💚"
        message = "Improvável... Mas milagres acontecem!"
        cor = 0x90ee90  # Verde claro
    else:
        emoji = "💔"
        message = "Péssimo! Melhor serem apenas amigos..."
        cor = 0x808080  # Cinza
    
    embed = discord.Embed(
        title=f'💘 SHIPAGEM: {ship_name.upper()}',
        description=f'**{user1.display_name}** {emoji} **{user2.display_name}**',
        color=cor
    )
    
    embed.add_field(
        name='📊 Compatibilidade',
        value=f'{bar}\\n**{ship_value}%**',
        inline=False
    )
    
    embed.add_field(
        name='💬 Resultado',
        value=message,
        inline=False
    )
    
    # Adiciona "curiosidades" aleatórias
    curiosidades = [
        "🎭 Opostos se atraem!",
        "🌟 A química é evidente!",
        "🔥 Que casal quente!",
        "❄️ Clima de frieza...",
        "⚡ A energia entre vocês é incrível!",
        "🌈 Amor colorido!",
        "💫 Conexão cósmica!",
        "🎪 Que palhaçada seria esse relacionamento!",
        "🎨 Vocês se complementam perfeitamente!",
        "🎵 Em harmonia total!"
    ]
    
    if ship_value >= 50:
        curiosidade = random.choice([c for c in curiosidades if not "frieza" in c.lower() and not "palhaçada" in c.lower()])
    else:
        curiosidade = random.choice(curiosidades)
    
    embed.add_field(
        name='✨ Análise',
        value=curiosidade,
        inline=False
    )
    
    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_ship, new_ship)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comando ship atualizado!")
