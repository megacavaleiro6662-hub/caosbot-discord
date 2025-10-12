#!/usr/bin/env python3
# Script para atualizar outros comandos e deixá-los mais detalhados

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== ABRAÇAR ====================
old_abracar = """@bot.command(name='abracar')
async def abracar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Você precisa mencionar alguém para abraçar! Exemplo: `.abracar @user`')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('🤗 *Você se abraça sozinho...*')
        return
    
    gif = random.choice(INTERACTION_GIFS['hug'])
    embed = discord.Embed(
        description=f'🤗 **{ctx.author.mention}** abraçou **{usuario.mention}**!',
        color=0xffd700
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_abracar = """@bot.command(name='abracar')
async def abracar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para abraçar!\\n\\n**Exemplo:**\\n`.abracar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='🤗 Auto-Abraço',
            description='Você se abraçou sozinho...\\n*Às vezes precisamos de carinho próprio!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não podem ser abraçados!\\n*Mas eles agradecem a intenção!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'🤗 **{ctx.author.mention}** deu um abraço apertado em **{usuario.mention}**!',
        f'🫂 **{ctx.author.mention}** abraçou **{usuario.mention}** carinhosamente!',
        f'💛 **{ctx.author.mention}** envolveu **{usuario.mention}** em um abraço caloroso!',
        f'🤗 **{ctx.author.mention}** deu um abraço de urso em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** abraçou **{usuario.mention}** com muito carinho!',
        f'💫 **{ctx.author.mention}** deu um abraço reconfortante em **{usuario.mention}**!'
    ]
    
    gif = random.choice(INTERACTION_GIFS['hug'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='🤗 Abraço Carinhoso',
        description=mensagem,
        color=0xffd700
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_abracar, new_abracar)

# ==================== ACARICIAR ====================
old_acariciar = """@bot.command(name='acariciar')
async def acariciar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Você precisa mencionar alguém para acariciar! Exemplo: `.acariciar @user`')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('😌 *Você faz carinho em si mesmo...*')
        return
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    embed = discord.Embed(
        description=f'😊 **{ctx.author.mention}** acariciou **{usuario.mention}**!',
        color=0x87ceeb
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_acariciar = """@bot.command(name='acariciar')
async def acariciar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para acariciar!\\n\\n**Exemplo:**\\n`.acariciar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😌 Auto-Carinho',
            description='Você faz carinho em si mesmo...\\n*Self-care é importante!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não sentem carinhos!\\n*Mas obrigado pela gentileza!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'😊 **{ctx.author.mention}** acariciou a cabeça de **{usuario.mention}**!',
        f'🥰 **{ctx.author.mention}** fez um carinho em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** deu head pat em **{usuario.mention}**!',
        f'💕 **{ctx.author.mention}** acariciou **{usuario.mention}** gentilmente!',
        f'🌸 **{ctx.author.mention}** fez cafuné em **{usuario.mention}**!',
        f'😌 **{ctx.author.mention}** acariciou **{usuario.mention}** com carinho!'
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='😊 Carinho Gentil',
        description=mensagem,
        color=0x87ceeb
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_acariciar, new_acariciar)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comandos abracar e acariciar atualizados!")
