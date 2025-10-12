#!/usr/bin/env python3
# Script para deixar embeds super detalhados com múltiplas mensagens

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== TAPA MAIS DETALHADO ====================
old_tapa_section = """    mensagens = [
        f'👋 **{ctx.author.mention}** deu um tapa na cara de **{usuario.mention}**!',
        f'💥 **{ctx.author.mention}** acertou um tapão em **{usuario.mention}**!',
        f'✋ **{ctx.author.mention}** esfregou a mão na cara de **{usuario.mention}**!',
        f'😤 **{ctx.author.mention}** deu uma bela palmada em **{usuario.mention}**!',
        f'🔥 **{ctx.author.mention}** mandou um tapa épico em **{usuario.mention}**!',
        f'💢 **{ctx.author.mention}** não perdoou e tapou **{usuario.mention}**!'
    ]
    
    gif = random.choice(INTERACTION_GIFS['slap'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='👋 Tapa Épico',
        description=mensagem,
        color=0xff4444
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

new_tapa_section = """    mensagens = [
        f'👋 **{ctx.author.mention}** deu um tapa na cara de **{usuario.mention}**!',
        f'💥 **{ctx.author.mention}** acertou um tapão monumental em **{usuario.mention}**!',
        f'✋ **{ctx.author.mention}** esfregou a mão na cara de **{usuario.mention}**!',
        f'😤 **{ctx.author.mention}** deu uma bela palmada em **{usuario.mention}**!',
        f'🔥 **{ctx.author.mention}** mandou um tapa épico em **{usuario.mention}**!',
        f'💢 **{ctx.author.mention}** não perdoou e tapou **{usuario.mention}**!',
        f'⚡ **{ctx.author.mention}** deu um tapa que ecoou no servidor em **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** acertou um super tapa em **{usuario.mention}**!',
        f'🌪️ **{ctx.author.mention}** mandou ver na cara de **{usuario.mention}**!',
        f'💪 **{ctx.author.mention}** mostrou quem manda com um tapa em **{usuario.mention}**!'
    ]
    
    reacoes = [
        "Isso deve ter doído!",
        "Que tapa sonoro!",
        "Ouvi o barulho daqui!",
        "Eita! Sem dó nem piedade!",
        "RIP a dignidade...",
        "Marcou até!",
        "Acho que acordou os vizinhos!",
        "Alguém chame a ambulância!",
        "Voou até!",
        "Que pancada!"
    ]
    
    gif = random.choice(INTERACTION_GIFS['slap'])
    mensagem = random.choice(mensagens)
    reacao = random.choice(reacoes)
    
    embed = discord.Embed(
        title='👋 Tapa Épico',
        description=mensagem,
        color=0xff4444
    )
    embed.add_field(
        name='💥 Reação',
        value=reacao,
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_tapa_section, new_tapa_section)

# ==================== DANÇAR MAIS DETALHADO ====================
old_dancar_solo = """        mensagens_solo = [
            f'💃 **{ctx.author.mention}** está dançando sozinho!',
            f'🕺 **{ctx.author.mention}** mandou ver nos passos!',
            f'✨ **{ctx.author.mention}** está arrasando na pista!',
            f'🎵 **{ctx.author.mention}** dançando como se ninguém estivesse olhando!',
            f'🌟 **{ctx.author.mention}** está fazendo um show solo!',
            f'💫 Que performance! **{ctx.author.mention}** dançando demais!'
        ]
        mensagem = random.choice(mensagens_solo)
        embed = discord.Embed(
            title='💃 Dança Solo',
            description=mensagem,
            color=0x9b59b6
        )"""

new_dancar_solo = """        mensagens_solo = [
            f'💃 **{ctx.author.mention}** está dançando sozinho!',
            f'🕺 **{ctx.author.mention}** mandou ver nos passos!',
            f'✨ **{ctx.author.mention}** está arrasando na pista!',
            f'🎵 **{ctx.author.mention}** dançando como se ninguém estivesse olhando!',
            f'🌟 **{ctx.author.mention}** está fazendo um show solo!',
            f'💫 Que performance! **{ctx.author.mention}** dançando demais!',
            f'🎪 **{ctx.author.mention}** está quebrando tudo na pista!',
            f'🔥 **{ctx.author.mention}** está dançando pra caramba!',
            f'⚡ **{ctx.author.mention}** mostrando seus melhores passos!',
            f'🌈 **{ctx.author.mention}** está se divertindo muito!'
        ]
        
        comentarios = [
            "Que energia incrível!",
            "Arrasou nos passos!",
            "Tá pegando fogo!",
            "Show de performance!",
            "Que talento!",
            "A pista é sua!",
            "Que ritmo maravilhoso!",
            "Está no flow!",
            "Mandou muito bem!",
            "Isso é arte!"
        ]
        
        mensagem = random.choice(mensagens_solo)
        comentario = random.choice(comentarios)
        
        embed = discord.Embed(
            title='💃 Dança Solo',
            description=mensagem,
            color=0x9b59b6
        )
        embed.add_field(
            name='🎭 Performance',
            value=comentario,
            inline=False
        )"""

content = content.replace(old_dancar_solo, new_dancar_solo)

# ==================== CHORAR MAIS DETALHADO ====================
old_chorar = """    mensagens = [
        f'😭 **{ctx.author.mention}** está chorando muito...',
        f'💧 **{ctx.author.mention}** não aguenta mais e chora...',
        f'😢 As lágrimas de **{ctx.author.mention}** não param de cair...',
        f'😿 **{ctx.author.mention}** está chorando copiosamente...',
        f'💔 **{ctx.author.mention}** chora de tristeza...',
        f'🥺 **{ctx.author.mention}** soltou as lágrimas...'
    ]
    
    gif = random.choice(INTERACTION_GIFS['cry'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='😭 Momento Triste',
        description=f'{mensagem}\\n\\n*Alguém console essa pessoa!*',
        color=0x5865f2
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

new_chorar = """    mensagens = [
        f'😭 **{ctx.author.mention}** está chorando muito...',
        f'💧 **{ctx.author.mention}** não aguenta mais e chora...',
        f'😢 As lágrimas de **{ctx.author.mention}** não param de cair...',
        f'😿 **{ctx.author.mention}** está chorando copiosamente...',
        f'💔 **{ctx.author.mention}** chora de tristeza...',
        f'🥺 **{ctx.author.mention}** soltou as lágrimas...',
        f'😭 **{ctx.author.mention}** está em prantos...',
        f'💧 **{ctx.author.mention}** chora sem parar...',
        f'😢 **{ctx.author.mention}** está muito emocionado...',
        f'🌧️ **{ctx.author.mention}** derramou lágrimas...'
    ]
    
    motivos = [
        "Parece que está triste hoje...",
        "Algo não está bem...",
        "O dia está difícil...",
        "Está precisando de apoio...",
        "Momento de desabafo...",
        "Deixa chorar, faz bem...",
        "Às vezes precisamos extravasar...",
        "Um abraço resolve...",
        "Console essa pessoa!",
        "Está precisando de carinho..."
    ]
    
    gif = random.choice(INTERACTION_GIFS['cry'])
    mensagem = random.choice(mensagens)
    motivo = random.choice(motivos)
    
    embed = discord.Embed(
        title='😭 Momento Triste',
        description=mensagem,
        color=0x5865f2
    )
    embed.add_field(
        name='💭 Situação',
        value=motivo,
        inline=False
    )
    embed.add_field(
        name='💝 Apoio',
        value='Envie um abraço ou carinho para essa pessoa! Use `.abracar` ou `.acariciar`',
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_chorar, new_chorar)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Embeds atualizados com mais detalhes e mensagens aleatorias!")
