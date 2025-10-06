# ========================================
# COMANDO .SCAN - ADICIONAR NO caosbot_railway.py
# ========================================
# COPIE TODO ESTE CÓDIGO E COLE APÓS O @restart_command.error
# (Linha 2453, antes do "# SISTEMA ANTI-SPAM")

@bot.command(name='scan')
@commands.has_permissions(administrator=True)
async def scan_server(ctx):
    """Escaneia e mostra TODOS os IDs do servidor (cargos, canais, categorias, etc)"""
    
    guild = ctx.guild
    
    # Criar arquivo de texto com todos os IDs
    scan_text = f"📊 SCAN COMPLETO DO SERVIDOR: {guild.name}\n"
    scan_text += f"=" * 60 + "\n\n"
    
    # CARGOS
    scan_text += "🏷️ CARGOS:\n"
    scan_text += "-" * 60 + "\n"
    for role in guild.roles:
        scan_text += f"Nome: {role.name}\n"
        scan_text += f"ID: {role.id}\n"
        scan_text += f"Cor: {role.color}\n"
        scan_text += f"Posição: {role.position}\n"
        scan_text += f"Mencionável: {role.mentionable}\n"
        scan_text += "-" * 60 + "\n"
    
    # CATEGORIAS DE CANAIS
    scan_text += "\n📁 CATEGORIAS:\n"
    scan_text += "-" * 60 + "\n"
    for category in guild.categories:
        scan_text += f"Nome: {category.name}\n"
        scan_text += f"ID: {category.id}\n"
        scan_text += f"Posição: {category.position}\n"
        scan_text += "-" * 60 + "\n"
    
    # CANAIS DE TEXTO
    scan_text += "\n💬 CANAIS DE TEXTO:\n"
    scan_text += "-" * 60 + "\n"
    for channel in guild.text_channels:
        scan_text += f"Nome: {channel.name}\n"
        scan_text += f"ID: {channel.id}\n"
        scan_text += f"Categoria: {channel.category.name if channel.category else 'Sem categoria'}\n"
        scan_text += f"Posição: {channel.position}\n"
        scan_text += "-" * 60 + "\n"
    
    # CANAIS DE VOZ
    scan_text += "\n🔊 CANAIS DE VOZ:\n"
    scan_text += "-" * 60 + "\n"
    for channel in guild.voice_channels:
        scan_text += f"Nome: {channel.name}\n"
        scan_text += f"ID: {channel.id}\n"
        scan_text += f"Categoria: {channel.category.name if channel.category else 'Sem categoria'}\n"
        scan_text += f"Posição: {channel.position}\n"
        scan_text += "-" * 60 + "\n"
    
    # EMOJIS
    scan_text += "\n😀 EMOJIS PERSONALIZADOS:\n"
    scan_text += "-" * 60 + "\n"
    for emoji in guild.emojis:
        scan_text += f"Nome: {emoji.name}\n"
        scan_text += f"ID: {emoji.id}\n"
        scan_text += f"Animado: {emoji.animated}\n"
        scan_text += "-" * 60 + "\n"
    
    # INFORMAÇÕES DO SERVIDOR
    scan_text += f"\n🌐 INFORMAÇÕES DO SERVIDOR:\n"
    scan_text += "-" * 60 + "\n"
    scan_text += f"Nome: {guild.name}\n"
    scan_text += f"ID: {guild.id}\n"
    scan_text += f"Dono: {guild.owner.name} (ID: {guild.owner.id})\n"
    scan_text += f"Região: {guild.preferred_locale}\n"
    scan_text += f"Membros: {guild.member_count}\n"
    scan_text += f"Criado em: {guild.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
    scan_text += "-" * 60 + "\n"
    
    # Salvar em arquivo
    filename = f"scan_{guild.id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(scan_text)
    
    # Enviar arquivo
    embed = discord.Embed(
        title="✅ SCAN COMPLETO FINALIZADO",
        description=f"Todos os IDs do servidor **{guild.name}** foram escaneados!",
        color=0x00ff00
    )
    embed.add_field(
        name="📊 Estatísticas",
        value=f"**Cargos:** {len(guild.roles)}\n"
              f"**Categorias:** {len(guild.categories)}\n"
              f"**Canais de Texto:** {len(guild.text_channels)}\n"
              f"**Canais de Voz:** {len(guild.voice_channels)}\n"
              f"**Emojis:** {len(guild.emojis)}\n"
              f"**Membros:** {guild.member_count}",
        inline=False
    )
    embed.set_footer(text="Sistema de Scan • Caos Hub")
    
    await ctx.reply(embed=embed, file=discord.File(filename))
    
    # Deletar arquivo local
    import os
    os.remove(filename)
    
    print(f"✅ Scan completo do servidor {guild.name} enviado para {ctx.author.name}")

@scan_server.error
async def scan_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar o comando .scan!")
