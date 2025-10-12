#!/usr/bin/env python3
# Script para atualizar GIFs e deixar comandos mais detalhados

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Atualizar GIFs de beijo
old_kiss = """    'kiss': [
        'https://media.tenor.com/W89cAX4VbYMAAAAM/anime-kiss.gif',
        'https://media.tenor.com/oAne0J6lj8MAAAAM/anime-kiss.gif',
        'https://media.tenor.com/pLDXlz1gN3gAAAAM/kiss-anime.gif',
        'https://media.tenor.com/jZVd4NKtw9UAAAAM/anime-kiss.gif',
        'https://media.tenor.com/0J5CXK5VvPcAAAAM/kiss-anime.gif'
    ]"""

new_kiss = """    'kiss': [
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FqBTvSNjNzeZG/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/MQVpBqASxSlFu/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/f82EqBTeCEgcU/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jR22gdcPiOLaE/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gTLfgIRwAiWOc/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/kU586ictpGb0Q/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/12VXIxKaIEarL2/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nyGFcsP0kAobm/giphy.gif'
    ]"""

content = content.replace(old_kiss, new_kiss)

# Atualizar comando .beijar para ser mais detalhado
old_beijar_cmd = """@bot.command(name='beijar')
async def beijar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Você precisa mencionar alguém para beijar! Exemplo: `.beijar @user`')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('😅 Você não pode se beijar!')
        return
    
    gif = random.choice(INTERACTION_GIFS['kiss'])
    embed = discord.Embed(
        description=f'💋 **{ctx.author.mention}** beijou **{usuario.mention}**!',
        color=0xff69b4
    )
    embed.set_image(url=gif)
    embed.set_footer(text=f'Comando usado por {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
    
    await ctx.reply(embed=embed)"""

new_beijar_cmd = """@bot.command(name='beijar')
async def beijar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para beijar!\\n\\n**Exemplo:**\\n`.beijar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😅 Ops!',
            description='Você não pode beijar a si mesmo!\\n*Tente beijar outra pessoa...*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Você não pode beijar um bot!\\n*Bots não têm sentimentos...*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    # Mensagens aleatórias
    mensagens = [
        f'💋 **{ctx.author.mention}** deu um beijo em **{usuario.mention}**!',
        f'😘 **{ctx.author.mention}** beijou **{usuario.mention}** de forma romântica!',
        f'💕 **{ctx.author.mention}** roubou um beijo de **{usuario.mention}**!',
        f'😍 **{ctx.author.mention}** beijou **{usuario.mention}** apaixonadamente!',
        f'❤️ **{ctx.author.mention}** deu um beijinho em **{usuario.mention}**!',
        f'💖 **{ctx.author.mention}** surpreendeu **{usuario.mention}** com um beijo!',
        f'🌹 **{ctx.author.mention}** beijou os lábios de **{usuario.mention}**!'
    ]
    
    gif = random.choice(INTERACTION_GIFS['kiss'])
    mensagem = random.choice(mensagens)
    
    embed = discord.Embed(
        title='💋 Beijo Romântico',
        description=mensagem,
        color=0xff1493
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)"""

content = content.replace(old_beijar_cmd, new_beijar_cmd)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("GIFs e comando .beijar atualizados com sucesso!")
