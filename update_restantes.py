#!/usr/bin/env python3
# Script para atualizar comandos restantes

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== TAPA ====================
old_tapa = """@bot.command(name='tapa')
async def tapa_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Você precisa mencionar alguém para dar um tapa! Exemplo: `.tapa @user`')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('🤕 Você se deu um tapa... Por quê?!')
        return
    
    gif = random.choice(INTERACTION_GIFS['slap'])
    embed = discord.Embed(
        description=f'👋 **{ctx.author.mention}** deu um tapa em **{usuario.mention}**!',
        color=0xff4444
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_tapa = """@bot.command(name='tapa')
async def tapa_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para dar um tapa!\\n\\n**Exemplo:**\\n`.tapa @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='🤕 Auto-Tapa',
            description='Você se deu um tapa... Por quê?!\\n*Isso deve ter doído!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Não bata em bots!\\n*Eles são inocentes!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
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

content = content.replace(old_tapa, new_tapa)

# ==================== DANÇAR ====================
old_dancar = """@bot.command(name='dancar')
async def dancar_command(ctx, usuario: discord.Member = None):
    gif = random.choice(INTERACTION_GIFS['dance'])
    
    if usuario:
        embed = discord.Embed(
            description=f'💃 **{ctx.author.mention}** está dançando com **{usuario.mention}**!',
            color=0x9b59b6
        )
    else:
        embed = discord.Embed(
            description=f'💃 **{ctx.author.mention}** está dançando!',
            color=0x9b59b6
        )
    
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_dancar = """@bot.command(name='dancar')
async def dancar_command(ctx, usuario: discord.Member = None):
    gif = random.choice(INTERACTION_GIFS['dance'])
    
    if usuario:
        if usuario.id == ctx.author.id:
            embed = discord.Embed(
                title='💃 Dança Solo',
                description=f'**{ctx.author.mention}** está dançando sozinho como se ninguém estivesse olhando!\\n*Que show!*',
                color=0x9b59b6
            )
        elif usuario.bot:
            embed = discord.Embed(
                title='🤖 Erro',
                description='Bots não dançam!\\n*Mas seria legal se dançassem...*',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return
        else:
            mensagens = [
                f'💃 **{ctx.author.mention}** está dançando com **{usuario.mention}**!',
                f'🕺 **{ctx.author.mention}** e **{usuario.mention}** estão arrasando na pista!',
                f'✨ **{ctx.author.mention}** chamou **{usuario.mention}** para dançar!',
                f'🎵 **{ctx.author.mention}** e **{usuario.mention}** dançam sincronizados!',
                f'🌟 Que dupla incrível! **{ctx.author.mention}** e **{usuario.mention}** mandando ver!',
                f'💫 **{ctx.author.mention}** rodou **{usuario.mention}** na pista de dança!'
            ]
            mensagem = random.choice(mensagens)
            embed = discord.Embed(
                title='💃 Dança em Dupla',
                description=mensagem,
                color=0x9b59b6
            )
    else:
        mensagens_solo = [
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
        )
    
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_dancar, new_dancar)

# ==================== CHORAR ====================
old_chorar = """@bot.command(name='chorar')
async def chorar_command(ctx):
    gif = random.choice(INTERACTION_GIFS['cry'])
    embed = discord.Embed(
        description=f'😭 **{ctx.author.mention}** está chorando...',
        color=0x5865f2
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_chorar = """@bot.command(name='chorar')
async def chorar_command(ctx):
    mensagens = [
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

content = content.replace(old_chorar, new_chorar)

# ==================== CAFUNÉ ====================
old_cafune = """@bot.command(name='cafune')
async def cafune_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Você precisa mencionar alguém para fazer cafuné! Exemplo: `.cafune @user`')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('😌 Você faz cafuné em si mesmo... Relaxante!')
        return
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    embed = discord.Embed(
        description=f'😌 **{ctx.author.mention}** está fazendo cafuné em **{usuario.mention}**!',
        color=0xffc0cb
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_cafune = """@bot.command(name='cafune')
async def cafune_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para fazer cafuné!\\n\\n**Exemplo:**\\n`.cafune @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😌 Auto-Cafuné',
            description='Você faz cafuné em si mesmo... Relaxante!\\n*Self-care extremo!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não têm cabelo para fazer cafuné!\\n*Mas agradecem pela intenção!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'😌 **{ctx.author.mention}** está fazendo cafuné em **{usuario.mention}**!',
        f'💆 **{ctx.author.mention}** acaricia a cabeça de **{usuario.mention}** suavemente!',
        f'✨ **{ctx.author.mention}** faz um cafuné relaxante em **{usuario.mention}**!',
        f'🌸 **{ctx.author.mention}** passa a mão no cabelo de **{usuario.mention}**!',
        f'💤 **{ctx.author.mention}** está fazendo **{usuario.mention}** relaxar com cafuné!',
        f'🥰 **{ctx.author.mention}** dá um cafuné carinhoso em **{usuario.mention}**!'
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='😌 Cafuné Relaxante',
        description=f'{mensagem}\\n\\n*Que momento de paz...*',
        color=0xffc0cb
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_cafune, new_cafune)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comandos tapa, dancar, chorar e cafune atualizados!")
