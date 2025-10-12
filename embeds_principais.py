#!/usr/bin/env python3
# Script para deixar embeds principais super detalhados

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== BEIJAR MAIS MENSAGENS ====================
old_beijar_msgs = """    # Mensagens aleatórias
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
    embed.set_image(url=gif)"""

new_beijar_msgs = """    # Mensagens aleatórias
    mensagens = [
        f'💋 **{ctx.author.mention}** deu um beijo em **{usuario.mention}**!',
        f'😘 **{ctx.author.mention}** beijou **{usuario.mention}** de forma romântica!',
        f'💕 **{ctx.author.mention}** roubou um beijo de **{usuario.mention}**!',
        f'😍 **{ctx.author.mention}** beijou **{usuario.mention}** apaixonadamente!',
        f'❤️ **{ctx.author.mention}** deu um beijinho em **{usuario.mention}**!',
        f'💖 **{ctx.author.mention}** surpreendeu **{usuario.mention}** com um beijo!',
        f'🌹 **{ctx.author.mention}** beijou os lábios de **{usuario.mention}**!',
        f'💝 **{ctx.author.mention}** selou os lábios de **{usuario.mention}** com um beijo!',
        f'✨ **{ctx.author.mention}** deu um beijo mágico em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** encheu **{usuario.mention}** de beijos!',
        f'💐 **{ctx.author.mention}** presenteou **{usuario.mention}** com um beijo!',
        f'🦋 **{ctx.author.mention}** deu um beijo delicado em **{usuario.mention}**!',
        f'🌺 **{ctx.author.mention}** beijou **{usuario.mention}** com paixão!'
    ]
    
    reacoes = [
        "Que momento romântico! 💕",
        "O amor está no ar! ❤️",
        "Shippo muito! 💖",
        "Que casal lindo! 😍",
        "Ahhh que fofo! 🥰",
        "Meu coração! 💗",
        "Amo esse casal! 💝",
        "Que beijo perfeito! 💋",
        "Tô morrendo de amor! 💘",
        "Casem logo! 💍"
    ]
    
    gif = random.choice(INTERACTION_GIFS['kiss'])
    mensagem = random.choice(mensagens)
    reacao = random.choice(reacoes)
    
    embed = discord.Embed(
        title='💋 Beijo Romântico',
        description=mensagem,
        color=0xff1493
    )
    embed.add_field(
        name='💕 Reação',
        value=reacao,
        inline=False
    )
    embed.set_image(url=gif)"""

content = content.replace(old_beijar_msgs, new_beijar_msgs)

# ==================== ABRAÇAR MAIS MENSAGENS ====================
old_abracar_msgs = """    mensagens = [
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
    embed.set_image(url=gif)"""

new_abracar_msgs = """    mensagens = [
        f'🤗 **{ctx.author.mention}** deu um abraço apertado em **{usuario.mention}**!',
        f'🫂 **{ctx.author.mention}** abraçou **{usuario.mention}** carinhosamente!',
        f'💛 **{ctx.author.mention}** envolveu **{usuario.mention}** em um abraço caloroso!',
        f'🤗 **{ctx.author.mention}** deu um abraço de urso em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** abraçou **{usuario.mention}** com muito carinho!',
        f'💫 **{ctx.author.mention}** deu um abraço reconfortante em **{usuario.mention}**!',
        f'🌟 **{ctx.author.mention}** abraçou **{usuario.mention}** com todo amor!',
        f'💝 **{ctx.author.mention}** deu um abraço protetor em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** abraçou **{usuario.mention}** fortemente!',
        f'🌈 **{ctx.author.mention}** envolveu **{usuario.mention}** em um abraço acolhedor!',
        f'🦋 **{ctx.author.mention}** abraçou **{usuario.mention}** com ternura!',
        f'🌸 **{ctx.author.mention}** deu um super abraço em **{usuario.mention}**!'
    ]
    
    sentimentos = [
        "Que abraço aconchegante! 🥰",
        "Abraço que aquece o coração! ❤️",
        "Amizade verdadeira! 💛",
        "Que momento lindo! ✨",
        "Abraços curam tudo! 💫",
        "Que carinho! 🤗",
        "Energia positiva! ⚡",
        "Abraço que reconforta! 💝",
        "Que fofura! 🥺",
        "Abraço perfeito! 🌟"
    ]
    
    gif = random.choice(INTERACTION_GIFS['hug'])
    mensagem = random.choice(mensagens)
    sentimento = random.choice(sentimentos)
    
    embed = discord.Embed(
        title='🤗 Abraço Carinhoso',
        description=mensagem,
        color=0xffd700
    )
    embed.add_field(
        name='💛 Sentimento',
        value=sentimento,
        inline=False
    )
    embed.set_image(url=gif)"""

content = content.replace(old_abracar_msgs, new_abracar_msgs)

# ==================== ACARICIAR MAIS MENSAGENS ====================
old_acariciar_msgs = """    mensagens = [
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
    embed.set_image(url=gif)"""

new_acariciar_msgs = """    mensagens = [
        f'😊 **{ctx.author.mention}** acariciou a cabeça de **{usuario.mention}**!',
        f'🥰 **{ctx.author.mention}** fez um carinho em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** deu head pat em **{usuario.mention}**!',
        f'💕 **{ctx.author.mention}** acariciou **{usuario.mention}** gentilmente!',
        f'🌸 **{ctx.author.mention}** fez cafuné em **{usuario.mention}**!',
        f'😌 **{ctx.author.mention}** acariciou **{usuario.mention}** com carinho!',
        f'🎀 **{ctx.author.mention}** passou a mão na cabeça de **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** deu um carinho delicado em **{usuario.mention}**!',
        f'🌺 **{ctx.author.mention}** acariciou **{usuario.mention}** suavemente!',
        f'🦋 **{ctx.author.mention}** fez um carinho relaxante em **{usuario.mention}**!',
        f'🌷 **{ctx.author.mention}** mimou **{usuario.mention}** com carinhos!',
        f'🌼 **{ctx.author.mention}** deu head pats em **{usuario.mention}**!'
    ]
    
    efeitos = [
        "Que relaxante! 😌",
        "Carinho gostoso! 🥰",
        "Tão fofo! 💕",
        "Que delícia! ✨",
        "Carinho que acalma! 💫",
        "Que mimo! 🌸",
        "Terapêutico! 💆",
        "Carinho perfeito! 🎀",
        "Que gentileza! 🌺",
        "Adorei! 😊"
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    efeito = random.choice(efeitos)
    
    embed = discord.Embed(
        title='😊 Carinho Gentil',
        description=mensagem,
        color=0x87ceeb
    )
    embed.add_field(
        name='💕 Efeito',
        value=efeito,
        inline=False
    )
    embed.set_image(url=gif)"""

content = content.replace(old_acariciar_msgs, new_acariciar_msgs)

# ==================== CAFUNÉ MAIS MENSAGENS ====================
old_cafune_msgs = """    mensagens = [
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
    embed.set_image(url=gif)"""

new_cafune_msgs = """    mensagens = [
        f'😌 **{ctx.author.mention}** está fazendo cafuné em **{usuario.mention}**!',
        f'💆 **{ctx.author.mention}** acaricia a cabeça de **{usuario.mention}** suavemente!',
        f'✨ **{ctx.author.mention}** faz um cafuné relaxante em **{usuario.mention}**!',
        f'🌸 **{ctx.author.mention}** passa a mão no cabelo de **{usuario.mention}**!',
        f'💤 **{ctx.author.mention}** está fazendo **{usuario.mention}** relaxar com cafuné!',
        f'🥰 **{ctx.author.mention}** dá um cafuné carinhoso em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** faz cafuné gostoso em **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** está mimando **{usuario.mention}** com cafuné!',
        f'🌺 **{ctx.author.mention}** dá um cafuné delicioso em **{usuario.mention}**!',
        f'🦋 **{ctx.author.mention}** faz cafuné que dá sono em **{usuario.mention}**!',
        f'🌷 **{ctx.author.mention}** está fazendo **{usuario.mention}** dormir com cafuné!',
        f'🌼 **{ctx.author.mention}** dá o melhor cafuné em **{usuario.mention}**!'
    ]
    
    beneficios = [
        "Que paz! 😌",
        "Puro relaxamento! 💆",
        "Quase dormindo... 💤",
        "Que delícia! 🥰",
        "Terapêutico! ✨",
        "Que carinho gostoso! 💕",
        "Relaxa demais! 🌸",
        "Melhor sensação! 💫",
        "Tão bom! 🎀",
        "Cafuné perfeito! 🌺"
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    beneficio = random.choice(beneficios)
    
    embed = discord.Embed(
        title='😌 Cafuné Relaxante',
        description=mensagem,
        color=0xffc0cb
    )
    embed.add_field(
        name='💆 Benefício',
        value=beneficio,
        inline=False
    )
    embed.add_field(
        name='✨ Momento',
        value='Momento de paz e relaxamento...',
        inline=False
    )
    embed.set_image(url=gif)"""

content = content.replace(old_cafune_msgs, new_cafune_msgs)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Embeds principais super detalhados com muitas mensagens!")
