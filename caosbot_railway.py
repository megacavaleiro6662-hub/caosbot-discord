# Bot Discord Caos - Python
# Arquivo principal do bot

import discord
from discord.ext import commands, tasks
import asyncio
import random
import time
import json
import os
from collections import defaultdict, deque
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import aiohttp
from datetime import datetime
from discord.ui import Button, View
import math
import threading
from flask import Flask

# ========================================
# SISTEMA DE MÚSICA REMOVIDO
# ========================================
# Bot focado em moderação, tickets e administração.
# Sistema de música foi removido para maior estabilidade e foco em vendas.

# ========================================
# SERVIDOR HTTP PARA RENDER (DETECTAR PORTA)
# ========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ CAOSBot está rodando!"

@app.route('/health')
def health():
    return {"status": "online", "bot": "CAOSBot", "lavalink": "active"}

def run_web():
    import os
    port = int(os.getenv("PORT", 10000))
    print(f'🌐 Servidor HTTP iniciado na porta {port}')
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# Iniciar servidor HTTP em thread separada
threading.Thread(target=run_web, daemon=True).start()

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # NECESSÁRIO para eventos de entrada/saída/ban
intents.presences = False  # Não precisa de presences

bot = commands.Bot(command_prefix='.', intents=intents)

# ========================================
# SISTEMA ANTI-HIBERNAÇÃO COMPLETO (100% GRATUITO)
# ========================================
# Este sistema mantém o bot online 24/7 no Render gratuitamente
# Funciona com UptimeRobot fazendo ping a cada 5 minutos

@tasks.loop(minutes=5)  # Ping interno a cada 5 minutos
async def keep_alive():
    """Mantém o bot sempre ativo - impede hibernação do Render"""
    try:
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f'💚 [{current_time}] Sistema anti-hibernação ativo! Bot online 24/7')
    except Exception as e:
        print(f'❌ Erro no sistema anti-hibernação: {e}')

@keep_alive.before_loop
async def before_keep_alive():
    """Aguarda o bot estar pronto antes de iniciar o sistema"""
    await bot.wait_until_ready()
    print('✅ Bot pronto! Sistema anti-hibernação ATIVADO!')
    print('🌐 Configure o UptimeRobot para pingar a URL do Render a cada 5 minutos')

# Evento quando o bot fica online
@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    print(f'📊 Conectado em {len(bot.guilds)} servidor(es)')
    print(f'🤖 Bot ID: {bot.user.id}')
    
    # Carregar dados das advertências
    load_warnings_data()
    
    # Carregar configurações de cargos
    load_role_config()
    
    # Carregar configurações de boas-vindas
    load_welcome_config()
    
    # INICIAR SISTEMA ANTI-HIBERNAÇÃO
    if not keep_alive.is_running():
        keep_alive.start()
        print('🔄 Sistema anti-hibernação ATIVADO! Bot ficará online 24/7')
    
    await bot.change_presence(
        activity=discord.Game(name=".play para música | O Hub dos sonhos"),
        status=discord.Status.online
    )

# ========================================
# EVENTOS DE BOAS-VINDAS/SAÍDA/BAN
# ========================================

@bot.event
async def on_member_join(member):
    """Evento quando alguém entra no servidor"""
    try:
        # Autorole
        if welcome_config['autorole_enabled']:
            role = member.guild.get_role(AUTOROLE_ID)
            if role:
                await member.add_roles(role)
                print(f"✅ Cargo {role.name} adicionado a {member.name}")
        
        # Boas-vindas
        if welcome_config['welcome_enabled']:
            channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"🎉 BEM-VINDO(A) AO {member.guild.name.upper()}!",
                    description=f"Olá {member.mention}! Seja muito bem-vindo(a) ao nosso servidor!\n\n🎭 Você agora é o **membro #{member.guild.member_count}**\n\n📜 Leia as regras e divirta-se!",
                    color=0xFFA500,  # LARANJA
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=WELCOME_GIF)
                embed.set_footer(text=f"ID: {member.id} • Sistema de Boas-vindas")
                
                await channel.send(embed=embed)
                print(f"👋 Boas-vindas enviadas para {member.name}")
                
    except Exception as e:
        print(f"❌ Erro no evento de entrada: {e}")

@bot.event
async def on_member_remove(member):
    """Evento quando alguém sai do servidor"""
    try:
        if welcome_config['goodbye_enabled']:
            # Verificar se o usuário foi banido (não mostrar mensagem de saída se foi ban)
            try:
                await member.guild.fetch_ban(member)
                # Se chegou aqui, o usuário foi banido - NÃO mostrar mensagem de saída
                print(f"🔨 {member.name} foi banido - pulando mensagem de saída")
                return
            except:
                # Usuário não foi banido, mostrar mensagem de saída normal
                pass
            
            channel = member.guild.get_channel(GOODBYE_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"👋 {member.name} SAIU DO SERVIDOR",
                    description=f"**{member.name}** saiu do servidor.\n\n😢 Esperamos que volte em breve!\n\n👥 Agora temos **{member.guild.member_count} membros**",
                    color=0x3498DB,  # AZUL
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=GOODBYE_GIF)
                embed.set_footer(text=f"ID: {member.id} • Sistema de Saída")
                
                await channel.send(embed=embed)
                print(f"👋 Mensagem de saída enviada para {member.name}")
                
    except Exception as e:
        print(f"❌ Erro no evento de saída: {e}")

# Evita loop de expulsão
ALREADY_KICKED = set()

@bot.event
async def on_voice_state_update(member, before, after):
    """Bloqueia bots de entrar em calls protegidas e mostra mensagem de kick"""
    try:
        # Ignorar membros que não estão na lista de bots bloqueados
        if member.id not in BLOCKED_BOTS:
            return

        # Ignorar se já foi expulso recentemente
        if member.id in ALREADY_KICKED:
            return

        # Verificar se entrou em um canal protegido
        if after.channel and after.channel.id in PROTECTED_VOICE_CHANNELS:
            # Garantir que realmente acabou de entrar
            if before.channel is None or before.channel.id != after.channel.id:
                await asyncio.sleep(0.5)

                try:
                    # Simula um "kick manual" no canal de voz
                    guild = member.guild
                    voice_state = member.voice
                    if voice_state and voice_state.channel:
                        # Remove o bot da call de forma que ele entenda como "kick"
                        await member.edit(voice_channel=None)
                        ALREADY_KICKED.add(member.id)
                        print(f"🚫 Bot {member.name} foi expulso da call {after.channel.name}")

                        # Aguardar 60s antes de liberar o ID novamente (evita loop)
                        await asyncio.sleep(60)
                        ALREADY_KICKED.discard(member.id)

                except Exception as e:
                    print(f"❌ Erro ao expulsar bot: {e}")

    except Exception as e:
        print(f"❌ Erro no evento de voz: {e}")

@bot.event
async def on_message(message):
    """Sistema de moderação automática e bloqueio de comandos"""
    # Ignorar mensagens do próprio bot
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    # ========================================
    # BLOQUEIO DE COMANDOS DE MÚSICA EM CALLS PROTEGIDAS
    # ========================================
    
    # Lista de comandos de música do Jockie
    music_commands = ['m!p', 'm!play', 'm!join', 'm!summon', 'm!connect']
    
    # Verificar se a mensagem começa com algum comando de música
    message_lower = message.content.lower()
    is_music_command = any(message_lower.startswith(cmd) for cmd in music_commands)
    
    if is_music_command:
        # Verificar se o usuário está em um canal de voz
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
            
            # Verificar se está em um canal protegido
            if voice_channel.id in PROTECTED_VOICE_CHANNELS:
                try:
                    # Deletar a mensagem do comando
                    await message.delete()
                    
                    # Enviar aviso
                    embed = discord.Embed(
                        title="🚫 COMANDO BLOQUEADO",
                        description=f"{message.author.mention}, você não pode usar comandos de música neste canal de voz!",
                        color=0xFF0000
                    )
                    embed.add_field(
                        name="❌ Canal Atual",
                        value=f"{voice_channel.mention}\n`Comandos de música bloqueados`",
                        inline=True
                    )
                    embed.add_field(
                        name="✅ Use nas Calls de Música",
                        value="Entre em um canal de música para usar o bot!",
                        inline=True
                    )
                    embed.set_footer(text="Sistema de Bloqueio • Caos Hub")
                    
                    # Enviar e deletar após 10 segundos
                    warning = await message.channel.send(embed=embed)
                    await asyncio.sleep(10)
                    await warning.delete()
                    
                    print(f"🚫 Comando de música bloqueado de {message.author.name} no canal {voice_channel.name}")
                    return
                    
                except Exception as e:
                    print(f"❌ Erro ao bloquear comando de música: {e}")
    
    # ========================================
    # IGNORAR MODERADORES PARA SISTEMAS DE PROTEÇÃO
    # ========================================
    
    # Ignorar moderadores (usuários com permissão de gerenciar mensagens)
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return
    
    # Processar outros comandos normalmente
    await bot.process_commands(message)

@bot.event
async def on_member_ban(guild, user):
    """Evento quando alguém é banido"""
    try:
        # Mensagem pública de ban (se ativado)
        if welcome_config['goodbye_enabled']:
            channel = guild.get_channel(GOODBYE_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"🔨 {user.name} FOI BANIDO!",
                    description=f"**{user.name}** foi banido do servidor.\n\n⚖️ Justiça foi feita!\n\n👥 Agora temos **{guild.member_count} membros**",
                    color=0xFF0000,  # VERMELHO
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_image(url=BAN_GIF)
                embed.set_footer(text=f"ID: {user.id} • Sistema de Banimento")
                
                await channel.send(embed=embed)
                print(f"🔨 Mensagem de ban enviada para {user.name}")
        
        # LOG DETALHADA DE BAN
        log_channel = guild.get_channel(BAN_LOG_CHANNEL_ID)
        if log_channel:
            # Buscar informações do ban
            try:
                ban_info = await guild.fetch_ban(user)
                reason = ban_info.reason or "Nenhum motivo fornecido"
            except:
                reason = "Não foi possível obter o motivo"
            
            # Buscar quem baniu (audit log)
            moderator = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
                    if entry.target.id == user.id:
                        moderator = entry.user
                        break
            except:
                pass
            
            # Criar embed detalhada
            log_embed = discord.Embed(
                title="🔨 USUÁRIO BANIDO",
                description=f"Um membro foi banido do servidor",
                color=0xFF0000,
                timestamp=datetime.now()
            )
            
            log_embed.add_field(
                name="👤 Usuário Banido",
                value=f"**Nome:** {user.name}\n**Tag:** {user.mention}\n**ID:** `{user.id}`",
                inline=True
            )
            
            if moderator:
                log_embed.add_field(
                    name="👮 Moderador",
                    value=f"**Nome:** {moderator.name}\n**Tag:** {moderator.mention}\n**ID:** `{moderator.id}`",
                    inline=True
                )
            else:
                log_embed.add_field(
                    name="👮 Moderador",
                    value="Não identificado",
                    inline=True
                )
            
            log_embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            log_embed.add_field(
                name="📝 Motivo",
                value=f"```{reason}```",
                inline=False
            )
            
            log_embed.add_field(
                name="📊 Informações Adicionais",
                value=f"**Conta criada em:** <t:{int(user.created_at.timestamp())}:F>\n**Membros restantes:** {guild.member_count}",
                inline=False
            )
            
            log_embed.set_thumbnail(url=user.display_avatar.url)
            log_embed.set_footer(text=f"Sistema de Logs • Ban ID: {user.id}")
            
            await log_channel.send(embed=log_embed)
            print(f"📋 Log de ban registrado para {user.name}")
                
    except Exception as e:
        print(f"❌ Erro no evento de ban: {e}")

# ========================================
# COMANDOS DE CONVERSA
# ========================================

@bot.command(name='oi')
async def oi_command(ctx):
    saudacoes = [
        'Oi! Como você está? 😊',
        'Olá! Tudo bem? 👋',
        'E aí! Beleza? 🤗',
        'Oi oi! Como foi seu dia? ✨',
        'Salve! Tudo certo? 🔥'
    ]
    resposta = random.choice(saudacoes)
    
    embed = discord.Embed(
        title="👋 Olá!",
        description=resposta,
        color=0x00ff88
    )
    embed.set_footer(text="Comandos de Conversa • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='comoesta')
async def comoesta_command(ctx, usuario: discord.Member = None):
    if usuario:
        embed = discord.Embed(
            title="🤔 Como você está?",
            description=f'{usuario.mention}, como você está hoje?',
            color=0x87ceeb
        )
    else:
        embed = discord.Embed(
            title="🤔 Como você está?",
            description='Como você está hoje?',
            color=0x87ceeb
        )
    embed.set_footer(text="Comandos de Conversa • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='conversa')
async def conversa_command(ctx):
    topicos = [
        'Qual foi a melhor parte do seu dia hoje?',
        'Se você pudesse ter qualquer superpoder, qual seria?',
        'Qual é sua comida favorita?',
        'Você prefere praia ou montanha?',
        'Qual filme você assistiria mil vezes?',
        'Se você pudesse viajar para qualquer lugar, onde seria?',
        'Qual é sua música favorita no momento?',
        'Você é mais de acordar cedo ou dormir tarde?',
        'Qual é seu hobby favorito?',
        'Se você pudesse jantar com qualquer pessoa, quem seria?'
    ]
    topico = random.choice(topicos)
    
    embed = discord.Embed(
        title="💭 Tópico de Conversa",
        description=topico,
        color=0xff69b4
    )
    embed.set_footer(text="Comandos de Conversa • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='clima')
async def clima_command(ctx):
    perguntas = [
        'Como está seu humor hoje? 😊',
        'Que energia você está sentindo hoje? ⚡',
        'Como você descreveria seu dia em uma palavra? 💭',
        'Está se sentindo bem hoje? 😌',
        'Qual é seu mood de hoje? 🎭'
    ]
    pergunta = random.choice(perguntas)
    
    embed = discord.Embed(
        title="🌤️ Como está seu clima?",
        description=pergunta,
        color=0xffd700
    )
    embed.set_footer(text="Comandos de Conversa • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='tchau')
async def tchau_command(ctx):
    despedidas = [
        'Tchau! Foi ótimo conversar com você! 👋',
        'Até mais! Cuide-se! 😊',
        'Falou! Volte sempre! 🤗',
        'Tchau tchau! Tenha um ótimo dia! ☀️',
        'Até a próxima! 👋✨'
    ]
    despedida = random.choice(despedidas)
    
    embed = discord.Embed(
        title="👋 Tchau!",
        description=despedida,
        color=0xff6b6b
    )
    embed.set_footer(text="Comandos de Conversa • Caos Hub")
    await ctx.reply(embed=embed)

# ========================================
# COMANDOS DE INTERAÇÃO
# ========================================

@bot.command(name='abraco')
async def abraco_command(ctx, usuario: discord.Member = None):
    abracos = [
        '🤗 *abraço apertado*',
        '🫂 *abraço carinhoso*',
        '🤗 *abraço virtual*',
        '🫂 *abraço de urso*',
        '🤗 *abraço reconfortante*'
    ]
    abraco = random.choice(abracos)
    
    if usuario:
        await ctx.reply(f'{abraco} para {usuario.mention}!')
    else:
        await ctx.reply(f'{abraco} para você!')

@bot.command(name='elogio')
async def elogio_command(ctx, usuario: discord.Member = None):
    elogios = [
        'Você é uma pessoa incrível! ✨',
        'Seu sorriso ilumina o dia de todo mundo! 😊',
        'Você tem uma energia muito positiva! 🌟',
        'Você é super inteligente! 🧠',
        'Sua presença sempre deixa tudo melhor! 💫',
        'Você é muito especial! 💖',
        'Você tem um coração gigante! ❤️',
        'Sua criatividade é inspiradora! 🎨',
        'Você sempre sabe o que dizer! 💬',
        'Você é uma pessoa única e especial! 🦄'
    ]
    elogio = random.choice(elogios)
    
    if usuario:
        await ctx.reply(f'{usuario.mention}, {elogio.lower()}')
    else:
        await ctx.reply(elogio)

@bot.command(name='motivacao')
async def motivacao_command(ctx):
    frases = [
        'Você é capaz de coisas incríveis! 💪',
        'Cada dia é uma nova oportunidade! 🌅',
        'Acredite em você mesmo! ⭐',
        'Você está indo muito bem! 👏',
        'Continue seguindo seus sonhos! 🌈',
        'Você é mais forte do que imagina! 💎',
        'Grandes coisas estão por vir! 🚀',
        'Você faz a diferença! 🌟',
        'Nunca desista dos seus objetivos! 🎯',
        'Você tem tudo para dar certo! 🍀'
    ]
    frase = random.choice(frases)
    await ctx.reply(f'🌟 {frase}')

# ========================================
# COMANDOS DE CONTROLE - BOAS-VINDAS/SAÍDA/BAN
# ========================================

@bot.command(name='setupwelcome')
@commands.has_permissions(administrator=True)
async def setup_welcome_command(ctx):
    """Ativa TODO o sistema de boas-vindas/saída/ban de uma vez"""
    
    # Ativar tudo EXCETO tickets (tickets precisa configurar separado)
    welcome_config['welcome_enabled'] = True
    welcome_config['goodbye_enabled'] = True
    welcome_config['autorole_enabled'] = True
    # NÃO ativa tickets automaticamente
    save_welcome_config()
    
    # Criar/atualizar painel
    await update_status_panel(ctx.guild)
    
    embed = discord.Embed(
        title="✅ SISTEMA ATIVADO COM SUCESSO!",
        description="O sistema de boas-vindas, saída/ban e autorole foi ativado!",
        color=0x00ff88
    )
    embed.add_field(
        name="📋 Configurações",
        value=f"👋 **Boas-vindas:** <#{WELCOME_CHANNEL_ID}>\n👋 **Saída/Ban:** <#{GOODBYE_CHANNEL_ID}>\n🎭 **Autorole:** <@&{AUTOROLE_ID}>\n📊 **Painel:** <#{STATUS_CHANNEL_ID}>",
        inline=False
    )
    embed.add_field(
        name="ℹ️ Tickets",
        value="Para ativar tickets, use `.ticket config` primeiro, depois `.toggletickets`",
        inline=False
    )
    embed.set_footer(text="Sistema de Eventos • Caos Hub")
    
    await ctx.reply(embed=embed)

@setup_welcome_command.error
async def setup_welcome_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

@bot.command(name='togglewelcome')
@commands.has_permissions(administrator=True)
async def toggle_welcome_command(ctx):
    """Liga/desliga sistema de boas-vindas"""
    
    welcome_config['welcome_enabled'] = not welcome_config['welcome_enabled']
    save_welcome_config()
    
    # Atualizar painel
    await update_status_panel(ctx.guild)
    
    status = "✅ **ATIVADO**" if welcome_config['welcome_enabled'] else "❌ **DESATIVADO**"
    
    embed = discord.Embed(
        title="🔄 BOAS-VINDAS ATUALIZADO",
        description=f"Sistema de boas-vindas: {status}",
        color=0x00ff88 if welcome_config['welcome_enabled'] else 0xff6b6b
    )
    embed.set_footer(text="Sistema de Eventos • Caos Hub")
    
    await ctx.reply(embed=embed)

@toggle_welcome_command.error
async def toggle_welcome_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

@bot.command(name='togglegoodbye')
@commands.has_permissions(administrator=True)
async def toggle_goodbye_command(ctx):
    """Liga/desliga sistema de saída/ban"""
    
    welcome_config['goodbye_enabled'] = not welcome_config['goodbye_enabled']
    save_welcome_config()
    
    # Atualizar painel
    await update_status_panel(ctx.guild)
    
    status = "✅ **ATIVADO**" if welcome_config['goodbye_enabled'] else "❌ **DESATIVADO**"
    
    embed = discord.Embed(
        title="🔄 SAÍDA/BAN ATUALIZADO",
        description=f"Sistema de saída/ban: {status}",
        color=0x00ff88 if welcome_config['goodbye_enabled'] else 0xff6b6b
    )
    embed.set_footer(text="Sistema de Eventos • Caos Hub")
    
    await ctx.reply(embed=embed)

@toggle_goodbye_command.error
async def toggle_goodbye_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

@bot.command(name='toggleautorole')
@commands.has_permissions(administrator=True)
async def toggle_autorole_command(ctx):
    """Liga/desliga sistema de autorole"""
    
    welcome_config['autorole_enabled'] = not welcome_config['autorole_enabled']
    save_welcome_config()
    
    # Atualizar painel
    await update_status_panel(ctx.guild)
    
    status = "✅ **ATIVADO**" if welcome_config['autorole_enabled'] else "❌ **DESATIVADO**"
    
    embed = discord.Embed(
        title="🔄 AUTOROLE ATUALIZADO",
        description=f"Sistema de autorole: {status}",
        color=0x00ff88 if welcome_config['autorole_enabled'] else 0xff6b6b
    )
    embed.set_footer(text="Sistema de Eventos • Caos Hub")
    
    await ctx.reply(embed=embed)

@toggle_autorole_command.error
async def toggle_autorole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

@bot.command(name='toggletickets')
@commands.has_permissions(administrator=True)
async def toggle_tickets_command(ctx):
    """Liga/desliga sistema de tickets"""
    
    welcome_config['tickets_enabled'] = not welcome_config['tickets_enabled']
    save_welcome_config()
    
    # Também atualizar o ticket_config se existir
    guild_id = str(ctx.guild.id)
    if 'ticket_config' in globals():
        if guild_id not in ticket_config:
            ticket_config[guild_id] = {
                'enabled': False,
                'category_id': None,
                'staff_role_ids': [],
                'welcome_message': 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.'
            }
        ticket_config[guild_id]['enabled'] = welcome_config['tickets_enabled']
        save_ticket_config()
    
    # Atualizar painel
    await update_status_panel(ctx.guild)
    
    status = "✅ **ATIVADO**" if welcome_config['tickets_enabled'] else "❌ **DESATIVADO**"
    
    embed = discord.Embed(
        title="🔄 TICKETS ATUALIZADO",
        description=f"Sistema de tickets: {status}",
        color=0x00ff88 if welcome_config['tickets_enabled'] else 0xff6b6b
    )
    
    # Adicionar info extra se tiver configuração
    if 'ticket_config' in globals() and guild_id in ticket_config:
        tconfig = ticket_config[guild_id]
        info_text = ""
        
        if tconfig.get('category_id'):
            category = ctx.guild.get_channel(tconfig['category_id'])
            info_text += f"📂 **Categoria:** {category.mention if category else '`Não encontrada`'}\n"
        
        if tconfig.get('staff_role_ids'):
            staff_roles = [ctx.guild.get_role(rid) for rid in tconfig['staff_role_ids']]
            staff_roles = [r for r in staff_roles if r]
            if staff_roles:
                info_text += f"👮 **Staff:** {', '.join([r.mention for r in staff_roles[:3]])}\n"
        
        if info_text:
            embed.add_field(name="📋 Configuração", value=info_text, inline=False)
        else:
            embed.add_field(
                name="⚠️ Aviso",
                value="Configure o sistema com `.ticket config` antes de usar!",
                inline=False
            )
    
    embed.set_footer(text="Sistema de Tickets • Caos Hub")
    
    await ctx.reply(embed=embed)

@toggle_tickets_command.error
async def toggle_tickets_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

# ========================================
# SISTEMA DE BLOQUEIO DE BOTS EM CALLS
# ========================================

@bot.command(name='blockedcalls')
@commands.has_permissions(administrator=True)
async def blocked_calls_command(ctx):
    """Mostra informações sobre o sistema de bloqueio de bots em calls"""
    
    embed = discord.Embed(
        title="🚫 SISTEMA DE BLOQUEIO DE BOTS",
        description="Sistema automático que impede bots específicos de entrar em canais de voz protegidos",
        color=0xFF0000,
        timestamp=datetime.now()
    )
    
    # Bots bloqueados
    blocked_bots_text = ""
    for bot_id in BLOCKED_BOTS:
        bot = ctx.guild.get_member(bot_id)
        if bot:
            blocked_bots_text += f"• {bot.mention} (`{bot.name}`)\n"
        else:
            blocked_bots_text += f"• ID: `{bot_id}` (não encontrado)\n"
    
    embed.add_field(
        name="🤖 Bots Bloqueados",
        value=blocked_bots_text or "Nenhum bot configurado",
        inline=False
    )
    
    # Canais protegidos
    protected_channels_text = ""
    for channel_id in PROTECTED_VOICE_CHANNELS:
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            protected_channels_text += f"• {channel.mention}\n"
        else:
            protected_channels_text += f"• ID: `{channel_id}` (não encontrado)\n"
    
    embed.add_field(
        name="🔒 Canais Protegidos",
        value=protected_channels_text or "Nenhum canal configurado",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Como Funciona",
        value="• Bloqueia comandos de música (`m!p`, `m!play`, etc)\n• Desconecta bot automaticamente se entrar\n• Sistema anti-loop com cooldown de 30s",
        inline=False
    )
    
    embed.set_footer(text="Sistema de Bloqueio • Caos Hub")
    
    await ctx.reply(embed=embed)

@blocked_calls_command.error
async def blocked_calls_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

@bot.command(name='config_bloqueio')
@commands.has_permissions(administrator=True)
async def config_bloqueio(ctx):
    """Configuração simplificada do sistema de bloqueio"""
    embed = discord.Embed(
        title="⚙️ Configuração do Sistema de Bloqueio",
        color=0x00FFFF,
        timestamp=datetime.now()
    )
    embed.add_field(
        name="🤖 Bots Bloqueados", 
        value="\n".join(f"`{b}`" for b in BLOCKED_BOTS),
        inline=False
    )
    embed.add_field(
        name="🔒 Canais Protegidos", 
        value="\n".join(f"`{c}`" for c in PROTECTED_VOICE_CHANNELS),
        inline=False
    )
    embed.set_footer(text="Sistema de Bloqueio • Caos Hub")
    await ctx.send(embed=embed)

@config_bloqueio.error
async def config_bloqueio_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

# ========================================
# COMANDOS DE MODERAÇÃO
# ========================================

# IDs dos cargos ADV
ADV_CARGO_1_ID = 1365861145738477598  # ADV 1
ADV_CARGO_2_ID = 1365861187392241714  # ADV 2
ADV_CARGO_3_ID = 1365861225900277832  # ADV 3

# ID do canal de logs
LOG_CHANNEL_ID = 1417638740435800186

# Arquivo para salvar dados das advertências
WARNINGS_FILE = "warnings_data.json"

# Dicionário para rastrear advertências dos usuários com detalhes completos
user_warnings = {}
user_warnings_details = {}  # Detalhes das advertências: motivo, moderador, timestamp

# Sistema de nicknames automáticos por cargo (configurado com IDs reais)
CARGO_PREFIXES = {
    # Cargos de moderação do servidor (IDs fornecidos pelo usuário)
    1365633918593794079: "[ADM]",  # Administrador
    1365634226254254150: "[STF]",  # Staff
    1365633102973763595: "[MOD]",  # Moderador
    1365631940434333748: "[SBM]",  # Sub Moderador
}

# Dicionário para salvar configurações de cargos
ROLE_CONFIG_FILE = "role_config.json"

# ========================================
# SISTEMA DE BOAS-VINDAS/SAÍDA/BAN
# ========================================

# Configurações fixas (IDs fornecidos pelo usuário)
WELCOME_CHANNEL_ID = 1365848708532535369  # Canal de entrada
GOODBYE_CHANNEL_ID = 1365848742355275886  # Canal de saída/ban
AUTOROLE_ID = 1365630916927553586  # Cargo Membro
STATUS_CHANNEL_ID = 1424157618447974471  # Canal do painel de status

# Canais de logs de moderação
KICK_LOG_CHANNEL_ID = 1417645057602752543  # Canal de log de kicks
BAN_LOG_CHANNEL_ID = 1417645081057558568  # Canal de log de bans

# Sistema de bloqueio de bots em calls
BLOCKED_BOTS = [
    411916947773587456,  # Jockie Music
    412347257233604609,  # Jockie 2
    412347553141751808   # Jockie 3
]

PROTECTED_VOICE_CHANNELS = [
    1365675025801412640,  # Call Voice 1
    1365678315905613855,  # Call Voice 2
    1365678337267208266,  # Call Voice 3
    1365678370917978256,  # Call Voice 4
    1365678387573817497,  # Call Voice 5
    1365678408637349891   # Call Voice 6
]

# GIFs
WELCOME_GIF = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWd3ZnNhYm0yN2p2M2UwcnZlY2k1bjNuYjg3b3dvZ3EyY2hhcHZjaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1n4iuWZFnTeN6qvdpD/giphy.gif"
GOODBYE_GIF = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmFwZjhxb2k2NnFwajloYXBjMDN2eTJmdzAwMGtmZnhobjNwYTBrayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QA7TPdyKJvj5Xdjm9A/giphy.gif"
BAN_GIF = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDE4YnhmZms4b29va2JxYnRubnI3cXVybzhsdWJsb3MxZmI3ZDB3eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nrXif9YExO9EI/giphy.gif"

# Arquivo de configuração
WELCOME_CONFIG_FILE = "welcome_config.json"

# Estado do sistema (ATIVADO automaticamente)
welcome_config = {
    'welcome_enabled': True,  # ✅ Boas-vindas SEMPRE ATIVAS
    'goodbye_enabled': True,  # ✅ Mensagem de saída SEMPRE ATIVA
    'autorole_enabled': True,  # ✅ Auto-cargo SEMPRE ATIVO
    'tickets_enabled': True,  # ✅ Sistema de tickets SEMPRE ATIVO
    'status_message_id': None
}

def save_welcome_config():
    """Salva configurações do sistema de boas-vindas"""
    try:
        with open(WELCOME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(welcome_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configurações de boas-vindas salvas")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações de boas-vindas: {e}")

def load_welcome_config():
    """Carrega configurações do sistema de boas-vindas"""
    global welcome_config
    try:
        if os.path.exists(WELCOME_CONFIG_FILE):
            with open(WELCOME_CONFIG_FILE, 'r', encoding='utf-8') as f:
                welcome_config = json.load(f)
            print(f"✅ Configurações de boas-vindas carregadas")
        else:
            print("📝 Arquivo de boas-vindas não encontrado, usando padrões")
    except Exception as e:
        print(f"❌ Erro ao carregar configurações de boas-vindas: {e}")

async def update_status_panel(guild):
    """Atualiza o painel de status do sistema"""
    try:
        status_channel = guild.get_channel(STATUS_CHANNEL_ID)
        if not status_channel:
            return
        
        # Pegar canais e cargo
        welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
        goodbye_channel = guild.get_channel(GOODBYE_CHANNEL_ID)
        autorole = guild.get_role(AUTOROLE_ID)
        
        # Criar embed do painel (COR PRETA)
        embed = discord.Embed(
            title="🎛️ PAINEL DE CONTROLE",
            description="**Sistema de Eventos e Automação**",
            color=0x000000,  # PRETO
            timestamp=datetime.now()
        )
        
        # Status Boas-vindas (COM CODE BLOCK)
        welcome_status = "Online" if welcome_config['welcome_enabled'] else "Offline"
        welcome_info = f"**Status**\n```{welcome_status}```\n**Canal:** {welcome_channel.mention if welcome_channel else '`Não configurado`'}"
        embed.add_field(
            name="👋 Boas-vindas",
            value=welcome_info,
            inline=True
        )
        
        # Status Saída/Ban (COM CODE BLOCK)
        goodbye_status = "Online" if welcome_config['goodbye_enabled'] else "Offline"
        goodbye_info = f"**Status**\n```{goodbye_status}```\n**Canal:** {goodbye_channel.mention if goodbye_channel else '`Não configurado`'}"
        embed.add_field(
            name="👋 Saída/Ban",
            value=goodbye_info,
            inline=True
        )
        
        # Espaço em branco para layout
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        # Status Autorole (COM CODE BLOCK)
        autorole_status = "Online" if welcome_config['autorole_enabled'] else "Offline"
        autorole_info = f"**Status**\n```{autorole_status}```\n**Cargo:** {autorole.mention if autorole else '`Não configurado`'}"
        embed.add_field(
            name="🎭 Autorole",
            value=autorole_info,
            inline=True
        )
        
        # Status Tickets (COM CODE BLOCK)
        tickets_status = "Online" if welcome_config['tickets_enabled'] else "Offline"
        
        # Pegar info do ticket_config se existir
        guild_id = str(guild.id)
        ticket_info_text = f"**Status**\n```{tickets_status}```"
        
        if 'ticket_config' in globals() and guild_id in ticket_config:
            tconfig = ticket_config[guild_id]
            if tconfig.get('category_id'):
                category = guild.get_channel(tconfig['category_id'])
                ticket_info_text += f"\n**Categoria:** {category.mention if category else '`Não encontrada`'}"
            
            if tconfig.get('staff_role_ids'):
                staff_roles = [guild.get_role(rid) for rid in tconfig['staff_role_ids']]
                staff_roles = [r for r in staff_roles if r]
                if staff_roles:
                    ticket_info_text += f"\n**Staff:** {staff_roles[0].mention}"
        
        embed.add_field(
            name="🎫 Tickets",
            value=ticket_info_text,
            inline=True
        )
        
        # Espaço em branco para layout
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        # Comandos disponíveis
        embed.add_field(
            name="⚙️ Comandos Disponíveis",
            value=(
                "**Configuração:**\n"
                "• `.setupwelcome` - Ativar eventos\n"
                "• `.ticket config` - Configurar tickets\n\n"
                "**Controles:**\n"
                "• `.togglewelcome` - Boas-vindas\n"
                "• `.togglegoodbye` - Saída/Ban\n"
                "• `.toggleautorole` - Autorole\n"
                "• `.toggletickets` - Tickets"
            ),
            inline=False
        )
        
        embed.set_footer(text="Sistema de Eventos • Caos Hub")
        
        # Atualizar ou criar mensagem
        if welcome_config['status_message_id']:
            try:
                msg = await status_channel.fetch_message(welcome_config['status_message_id'])
                await msg.edit(embed=embed)
            except:
                # Se não encontrar, criar nova
                msg = await status_channel.send(embed=embed)
                welcome_config['status_message_id'] = msg.id
                save_welcome_config()
        else:
            # Criar nova mensagem
            msg = await status_channel.send(embed=embed)
            welcome_config['status_message_id'] = msg.id
            save_welcome_config()
            
    except Exception as e:
        print(f"❌ Erro ao atualizar painel de status: {e}")

def save_role_config():
    """Salva configurações de cargos em arquivo JSON"""
    try:
        data = {
            'cargo_prefixes': {str(k): v for k, v in CARGO_PREFIXES.items()}
        }
        with open(ROLE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Configurações de cargos salvas em {ROLE_CONFIG_FILE}")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações de cargos: {e}")

def load_role_config():
    """Carrega configurações de cargos do arquivo JSON"""
    global CARGO_PREFIXES
    try:
        if os.path.exists(ROLE_CONFIG_FILE):
            with open(ROLE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converter chaves de string para int
            loaded_prefixes = {int(k): v for k, v in data.get('cargo_prefixes', {}).items()}
            CARGO_PREFIXES.update(loaded_prefixes)
            
            print(f"✅ Configurações de cargos carregadas: {len(CARGO_PREFIXES)} cargos")
        else:
            print("📝 Arquivo de configuração de cargos não encontrado, usando padrões")
    except Exception as e:
        print(f"❌ Erro ao carregar configurações de cargos: {e}")

# Armazenar nicknames originais
original_nicknames = {}

def save_warnings_data():
    """Salva os dados das advertências em arquivo JSON"""
    try:
        data = {
            'user_warnings': user_warnings,
            'user_warnings_details': {}
        }
        
        # Converter timestamps para string para serialização JSON
        for user_id, details_list in user_warnings_details.items():
            data['user_warnings_details'][str(user_id)] = []
            for detail in details_list:
                detail_copy = detail.copy()
                if 'timestamp' in detail_copy:
                    detail_copy['timestamp'] = detail_copy['timestamp'].isoformat()
                data['user_warnings_details'][str(user_id)].append(detail_copy)
        
        with open(WARNINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados das advertências salvos em {WARNINGS_FILE}")
    except Exception as e:
        print(f"❌ Erro ao salvar dados das advertências: {e}")

def load_warnings_data():
    """Carrega os dados das advertências do arquivo JSON"""
    global user_warnings, user_warnings_details
    
    try:
        if os.path.exists(WARNINGS_FILE):
            with open(WARNINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_warnings = data.get('user_warnings', {})
            # Converter chaves de string para int
            user_warnings = {int(k): v for k, v in user_warnings.items()}
            
            user_warnings_details = {}
            details_data = data.get('user_warnings_details', {})
            
            # Converter timestamps de volta para datetime
            import datetime
            for user_id_str, details_list in details_data.items():
                user_id = int(user_id_str)
                user_warnings_details[user_id] = []
                for detail in details_list:
                    if 'timestamp' in detail and isinstance(detail['timestamp'], str):
                        detail['timestamp'] = datetime.datetime.fromisoformat(detail['timestamp'])
                    user_warnings_details[user_id].append(detail)
            
            print(f"✅ Dados das advertências carregados: {len(user_warnings)} usuários")
        else:
            print("📝 Arquivo de advertências não encontrado, iniciando com dados vazios")
            
    except Exception as e:
        print(f"❌ Erro ao carregar dados das advertências: {e}")
        user_warnings = {}
        user_warnings_details = {}

# ID do cargo de mute
MUTE_ROLE_ID = None  # Será criado automaticamente

# ID do cargo de Sub Moderador (substitua pelo ID correto)
SUB_MODERADOR_ROLE_ID = None  # Coloque o ID do cargo aqui

def is_sub_moderator_or_higher():
    """Decorator personalizado para verificar se o usuário é sub moderador ou tem permissões superiores"""
    async def predicate(ctx):
        # Verificar se é administrador
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Verificar se tem permissões de moderação padrão
        if (ctx.author.guild_permissions.manage_roles or 
            ctx.author.guild_permissions.kick_members or 
            ctx.author.guild_permissions.ban_members or
            ctx.author.guild_permissions.manage_messages):
            return True
        
        # Verificar se tem o cargo de Sub Moderador
        if SUB_MODERADOR_ROLE_ID:
            sub_mod_role = ctx.guild.get_role(SUB_MODERADOR_ROLE_ID)
            if sub_mod_role and sub_mod_role in ctx.author.roles:
                return True
        
        # Se não tem nenhuma das condições acima, negar acesso
        return False
    
    return commands.check(predicate)

# Sistemas de proteção
message_history = defaultdict(lambda: deque(maxlen=5))  # Últimas 5 mensagens por usuário
user_message_times = defaultdict(lambda: deque(maxlen=5))  # Timestamps das mensagens
spam_warnings = defaultdict(int)  # Avisos de spam por usuário (0=5msgs, 1=4msgs, 2+=3msgs)

async def get_or_create_mute_role(guild):
    """Obtém ou cria o cargo de mute"""
    global MUTE_ROLE_ID
    
    # Se já temos o ID salvo, tentar usar ele primeiro
    if MUTE_ROLE_ID:
        mute_role = guild.get_role(MUTE_ROLE_ID)
        if mute_role:
            return mute_role
    
    # Procurar cargo existente por nome
    mute_role = discord.utils.get(guild.roles, name="Muted")
    
    # Se não encontrou, procurar por outros nomes comuns
    if not mute_role:
        common_names = ["Muted", "Mutado", "Silenciado", "Mute"]
        for name in common_names:
            mute_role = discord.utils.get(guild.roles, name=name)
            if mute_role:
                break
    
    if not mute_role:
        try:
            # Criar cargo de mute
            mute_role = await guild.create_role(
                name="Muted",
                color=discord.Color.dark_gray(),
                reason="Cargo de mute criado automaticamente pelo bot"
            )
            
            print(f"✅ Cargo 'Muted' criado com ID: {mute_role.id}")
            
            # Configurar permissões em todos os canais
            channels_configured = 0
            for channel in guild.channels:
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
                        channels_configured += 1
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(mute_role, speak=False, connect=False)
                        channels_configured += 1
                except Exception as e:
                    print(f"Erro ao configurar permissões no canal {channel.name}: {e}")
                    continue
            
            print(f"✅ Permissões configuradas em {channels_configured} canais")
                    
        except Exception as e:
            print(f"❌ Erro ao criar cargo de mute: {e}")
            return None
    
    # Salvar o ID para uso futuro
    MUTE_ROLE_ID = mute_role.id
    return mute_role

async def send_adv_log(ctx, usuario, motivo, warning_count, action_type="advertencia"):
    """Envia log detalhado de advertência para o canal específico"""
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return
        
        # Definir cores e ícones baseado no nível
        if warning_count == 1:
            color = 0xffff00  # Amarelo
            level_icon = "🟡"
            level_name = "ADV 1"
            level_desc = "Primeira Advertência"
            threat_level = "BAIXO"
        elif warning_count == 2:
            color = 0xff8c00  # Laranja
            level_icon = "🟠"
            level_name = "ADV 2"
            level_desc = "Segunda Advertência"
            threat_level = "MÉDIO"
        else:
            color = 0xff0000  # Vermelho
            level_icon = "🔴"
            level_name = "ADV 3"
            level_desc = "Terceira Advertência + Ban"
            threat_level = "CRÍTICO"
        
        # Criar embed principal
        if action_type == "advertencia":
            embed = discord.Embed(
                title=f"🚨 SISTEMA DE ADVERTÊNCIAS - {level_desc.upper()}",
                description=f"{level_icon} **{level_name}** aplicada com sucesso",
                color=color,
                timestamp=ctx.message.created_at
            )
        else:  # remoção
            if warning_count == 0:
                embed = discord.Embed(
                    title="🧹 SISTEMA DE ADVERTÊNCIAS - REMOÇÃO TOTAL",
                    description="✅ **Todas as advertências removidas** com sucesso",
                    color=0x00ff00,
                    timestamp=ctx.message.created_at
                )
            else:
                embed = discord.Embed(
                    title="🔄 SISTEMA DE ADVERTÊNCIAS - REDUÇÃO",
                    description="✅ **Advertência removida** com sucesso",
                    color=0x00ff00,
                    timestamp=ctx.message.created_at
                )
        
        # Informações do usuário punido
        embed.add_field(
            name="👤 USUÁRIO PUNIDO",
            value=f"**Nome:** {usuario.display_name}\n**Tag:** {usuario.name}#{usuario.discriminator}\n**ID:** `{usuario.id}`\n**Menção:** {usuario.mention}",
            inline=True
        )
        
        # Informações do moderador
        embed.add_field(
            name="👮 MODERADOR",
            value=f"**Nome:** {ctx.author.display_name}\n**Tag:** {ctx.author.name}#{ctx.author.discriminator}\n**ID:** `{ctx.author.id}`\n**Menção:** {ctx.author.mention}",
            inline=True
        )
        
        if action_type == "advertencia":
            # Nível de ameaça
            embed.add_field(
                name="⚠️ NÍVEL DE AMEAÇA",
                value=f"**Status:** {threat_level}\n**Advertências:** {warning_count}/3\n**Próxima ação:** {'Ban automático' if warning_count >= 2 else f'ADV {warning_count + 1}'}",
                inline=True
            )
        
        # Motivo detalhado
        embed.add_field(
            name="📝 MOTIVO DA AÇÃO",
            value=f"```{motivo}```",
            inline=False
        )
        
        if action_type == "advertencia":
            # Detalhes da punição
            if warning_count == 1:
                punishment_details = f"🟡 **Cargo aplicado:** <@&{ADV_CARGO_1_ID}>\n⚠️ **Consequência:** Aviso inicial\n📢 **Orientação:** Melhore a conduta"
            elif warning_count == 2:
                punishment_details = f"🟠 **Cargo aplicado:** <@&{ADV_CARGO_2_ID}>\n🚨 **Consequência:** Advertência séria\n⚠️ **Orientação:** ÚLTIMA CHANCE"
            else:
                punishment_details = f"🔴 **Cargo aplicado:** <@&{ADV_CARGO_3_ID}>\n💀 **Consequência:** Banimento automático\n🚫 **Status:** Usuário removido"
            
            embed.add_field(
                name="⚖️ DETALHES DA PUNIÇÃO",
                value=punishment_details,
                inline=False
            )
        
        # Informações do servidor
        embed.add_field(
            name="🏠 INFORMAÇÕES DO SERVIDOR",
            value=f"**Servidor:** {ctx.guild.name}\n**Canal:** #{ctx.channel.name}\n**Comando:** `{ctx.message.content.split()[0]}`",
            inline=True
        )
        
        # Informações técnicas
        embed.add_field(
            name="🔧 INFORMAÇÕES TÉCNICAS",
            value=f"**Timestamp:** <t:{int(ctx.message.created_at.timestamp())}:F>\n**Message ID:** `{ctx.message.id}`\n**Sistema:** Caos Bot v2.0",
            inline=True
        )
        
        if action_type == "advertencia" and warning_count >= 3:
            # Informações do ban
            embed.add_field(
                name="🔨 DETALHES DO BANIMENTO",
                value=f"**Motivo do ban:** 3 advertências atingidas\n**Tipo:** Automático\n**Reversível:** Não\n**Data:** <t:{int(ctx.message.created_at.timestamp())}:F>",
                inline=False
            )
        
        # Footer personalizado
        embed.set_footer(
            text=f"Sistema de Moderação • Caos Hub | Log ID: {ctx.message.id}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Thumbnail do usuário
        embed.set_thumbnail(url=usuario.display_avatar.url)
        
        # Autor do embed
        embed.set_author(
            name=f"Ação executada por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await log_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

@bot.command(name='adv')
@is_sub_moderator_or_higher()
async def adv_command(ctx, usuario: discord.Member = None, *, motivo=None):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `.adv @usuário [motivo]`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    # Definir motivo padrão se não fornecido
    if motivo is None:
        motivo = "Sem motivo especificado"
    
    # Verificar se o usuário já tem advertências
    user_id = usuario.id
    if user_id not in user_warnings:
        user_warnings[user_id] = 0
    
    user_warnings[user_id] += 1
    warning_count = user_warnings[user_id]
    
    # Salvar detalhes da advertência
    if user_id not in user_warnings_details:
        user_warnings_details[user_id] = []
    
    import datetime
    user_warnings_details[user_id].append({
        'level': warning_count,
        'motivo': motivo,
        'moderador': ctx.author.display_name,
        'moderador_id': ctx.author.id,
        'timestamp': datetime.datetime.now(),
        'channel': ctx.channel.name
    })
    
    # Salvar dados no arquivo
    save_warnings_data()
    
    try:
        if warning_count == 1:
            # Primeira advertência - ADV 1
            cargo = ctx.guild.get_role(ADV_CARGO_1_ID)
            if cargo:
                await usuario.add_roles(cargo)
                
                embed = discord.Embed(
                    title="⚠️ PRIMEIRA ADVERTÊNCIA",
                    description=f"**{usuario.display_name}** recebeu sua primeira advertência!",
                    color=0xffff00
                )
                embed.add_field(
                    name="📋 Detalhes",
                    value="🟡 **ADV 1** - Aviso inicial\n⚠️ Comportamento inadequado detectado\n📢 Melhore sua conduta no servidor!",
                    inline=False
                )
                embed.add_field(
                    name="📝 Motivo",
                    value=f"`{motivo}`",
                    inline=False
                )
                embed.add_field(
                    name="⏭️ Próximo Nível",
                    value="🟠 **ADV 2** - Advertência séria",
                    inline=True
                )
                embed.add_field(
                    name="👤 Usuário",
                    value=usuario.mention,
                    inline=True
                )
                embed.add_field(
                    name="👮 Moderador",
                    value=ctx.author.mention,
                    inline=True
                )
                embed.set_footer(text="Sistema de Advertências • Caos Hub")
                await ctx.reply(embed=embed)
                
                # Enviar log detalhado
                await send_adv_log(ctx, usuario, motivo, warning_count)
            else:
                await ctx.reply("❌ Cargo ADV 1 não encontrado!")
                
        elif warning_count == 2:
            # Segunda advertência - ADV 2 (remove ADV 1)
            cargo_antigo = ctx.guild.get_role(ADV_CARGO_1_ID)
            cargo_novo = ctx.guild.get_role(ADV_CARGO_2_ID)
            
            if cargo_antigo and cargo_antigo in usuario.roles:
                await usuario.remove_roles(cargo_antigo)
            
            if cargo_novo:
                await usuario.add_roles(cargo_novo)
                
                embed = discord.Embed(
                    title="🚨 SEGUNDA ADVERTÊNCIA",
                    description=f"**{usuario.display_name}** está em situação crítica!",
                    color=0xff8c00
                )
                embed.add_field(
                    name="📋 Detalhes",
                    value="🟠 **ADV 2** - Advertência séria\n🚨 Comportamento persistente inadequado\n⚠️ ÚLTIMA CHANCE antes do banimento!",
                    inline=False
                )
                embed.add_field(
                    name="📝 Motivo",
                    value=f"`{motivo}`",
                    inline=False
                )
                embed.add_field(
                    name="⏭️ Próximo Nível",
                    value="🔴 **ADV 3** - BANIMENTO AUTOMÁTICO",
                    inline=True
                )
                embed.add_field(
                    name="👤 Usuário",
                    value=usuario.mention,
                    inline=True
                )
                embed.add_field(
                    name="👮 Moderador",
                    value=ctx.author.mention,
                    inline=True
                )
                embed.set_footer(text="Sistema de Advertências • Caos Hub")
                await ctx.reply(embed=embed)
                
                # Enviar log detalhado
                await send_adv_log(ctx, usuario, motivo, warning_count)
            else:
                await ctx.reply("❌ Cargo ADV 2 não encontrado!")
                
        elif warning_count >= 3:
            # Terceira advertência - BAN (remove cargos anteriores)
            cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
            cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
            cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
            
            # Remover cargos anteriores
            if cargo_adv1 and cargo_adv1 in usuario.roles:
                await usuario.remove_roles(cargo_adv1)
            if cargo_adv2 and cargo_adv2 in usuario.roles:
                await usuario.remove_roles(cargo_adv2)
            
            if cargo_adv3:
                await usuario.add_roles(cargo_adv3)
            
            embed = discord.Embed(
                title="🔨 BANIMENTO AUTOMÁTICO",
                description=f"**{usuario.display_name}** foi banido do servidor!",
                color=0xff0000
            )
            embed.add_field(
                name="📋 Detalhes",
                value="🔴 **ADV 3** - Banimento definitivo\n💀 Três advertências atingidas\n🚫 Usuário removido permanentemente",
                inline=False
            )
            embed.add_field(
                name="📝 Motivo Final",
                value=f"`{motivo}`",
                inline=False
            )
            embed.add_field(
                name="⚖️ Motivo do Ban",
                value="3 advertências - Ban automático",
                inline=True
            )
            embed.add_field(
                name="👤 Usuário Banido",
                value=f"{usuario.mention}\n`{usuario.id}`",
                inline=True
            )
            embed.add_field(
                name="👮 Moderador",
                value=ctx.author.mention,
                inline=True
            )
            embed.set_footer(text="Sistema de Advertências • Caos Hub")
            await ctx.reply(embed=embed)
            
            # Enviar log detalhado
            await send_adv_log(ctx, usuario, motivo, warning_count)
            
            # Banir o usuário
            await usuario.ban(reason=f"3 advertências - Ban automático | Último motivo: {motivo}")
            
            # Resetar contador
            user_warnings[user_id] = 0
            
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para gerenciar cargos ou banir usuários!")
    except Exception as e:
        await ctx.reply(f"❌ Erro ao aplicar advertência: {e}")

@adv_command.error
async def adv_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='radv')
@is_sub_moderator_or_higher()
async def radv_command(ctx, usuario: discord.Member = None):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!radv @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    user_id = usuario.id
    
    # Verificar se o usuário tem advertências
    if user_id not in user_warnings or user_warnings[user_id] == 0:
        embed = discord.Embed(
            title="ℹ️ Sem Advertências",
            description=f"**{usuario.display_name}** não possui advertências para remover.",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    try:
        current_warnings = user_warnings[user_id]
        new_warnings = current_warnings - 1
        
        # Determinar qual cargo remover e qual aplicar
        cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
        cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
        cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
        
        cargo_removido = ""
        cargo_aplicado = ""
        
        if current_warnings == 3:
            # De ADV 3 para ADV 2
            if cargo_adv3 and cargo_adv3 in usuario.roles:
                await usuario.remove_roles(cargo_adv3)
                cargo_removido = "ADV 3"
            if cargo_adv2:
                await usuario.add_roles(cargo_adv2)
                cargo_aplicado = "ADV 2"
        elif current_warnings == 2:
            # De ADV 2 para ADV 1
            if cargo_adv2 and cargo_adv2 in usuario.roles:
                await usuario.remove_roles(cargo_adv2)
                cargo_removido = "ADV 2"
            if cargo_adv1:
                await usuario.add_roles(cargo_adv1)
                cargo_aplicado = "ADV 1"
        elif current_warnings == 1:
            # De ADV 1 para sem advertência
            if cargo_adv1 and cargo_adv1 in usuario.roles:
                await usuario.remove_roles(cargo_adv1)
                cargo_removido = "ADV 1"
            cargo_aplicado = "Nenhum"
        
        # Atualizar contador
        user_warnings[user_id] = new_warnings
        
        embed = discord.Embed(
            title="✅ ADVERTÊNCIA REMOVIDA",
            description=f"**{usuario.display_name}** teve 1 advertência removida!",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"🔄 **Advertências:** {current_warnings} → {new_warnings}\n🗑️ **Cargo removido:** {cargo_removido}\n✨ **Cargo atual:** {cargo_aplicado}\n📉 Nível de advertência reduzido!",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        
        # Enviar log de remoção
        await send_adv_log(ctx, usuario, f"Advertência removida: {current_warnings} → {new_warnings}", new_warnings, "remocao")
        
        # Salvar dados no arquivo
        save_warnings_data()
        
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para gerenciar cargos!")
    except Exception as e:
        await ctx.reply(f"❌ Erro ao remover advertências: {e}")

@radv_command.error
async def radv_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='radvall')
@is_sub_moderator_or_higher()
async def radvall_command(ctx, usuario: discord.Member = None):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!radvall @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    user_id = usuario.id
    
    # DETECÇÃO INTELIGENTE - Verificar cargos reais do usuário
    cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
    cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
    cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
    
    tem_adv = False
    if (cargo_adv1 and cargo_adv1 in usuario.roles) or \
       (cargo_adv2 and cargo_adv2 in usuario.roles) or \
       (cargo_adv3 and cargo_adv3 in usuario.roles):
        tem_adv = True
    
    # Verificar se o usuário tem advertências (cargos OU contador)
    if not tem_adv and (user_id not in user_warnings or user_warnings[user_id] == 0):
        embed = discord.Embed(
            title="ℹ️ Sem Advertências",
            description=f"**{usuario.display_name}** não possui advertências para remover.",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    try:
        # Guardar quantas ADVs tinha
        advs_anteriores = user_warnings.get(user_id, 0)
        
        # Remover cargos
        roles_removidos = []
        
        if cargo_adv1 and cargo_adv1 in usuario.roles:
            await usuario.remove_roles(cargo_adv1, reason=f"Todas ADVs removidas por {ctx.author}")
            roles_removidos.append("ADV 1")
        
        if cargo_adv2 and cargo_adv2 in usuario.roles:
            await usuario.remove_roles(cargo_adv2, reason=f"Todas ADVs removidas por {ctx.author}")
            roles_removidos.append("ADV 2")
        
        if cargo_adv3 and cargo_adv3 in usuario.roles:
            await usuario.remove_roles(cargo_adv3, reason=f"Todas ADVs removidas por {ctx.author}")
            roles_removidos.append("ADV 3")
        
        # Resetar contador
        user_warnings[user_id] = 0
        save_warnings_data()
        
        embed = discord.Embed(
            title="🧹 TODAS ADVERTÊNCIAS REMOVIDAS",
            description=f"**{usuario.display_name}** teve TODAS as advertências removidas!",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"🧹 **Advertências anteriores:** {advs_anteriores}\n✨ **Cargos removidos:** {', '.join(roles_removidos) if roles_removidos else 'Nenhum'}\n🎉 Usuário com ficha limpa!",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        
        # Enviar log de remoção total
        await send_adv_log(ctx, usuario, "Todas as advertências removidas pelo moderador", 0, "remocao")
        
        # Salvar dados no arquivo
        save_warnings_data()
        
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para gerenciar cargos!")
    except Exception as e:
        await ctx.reply(f"❌ Erro ao remover advertências: {e}")

@radvall_command.error
async def radvall_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

# COMANDO SEEADV REMOVIDO - ESTAVA BUGADO

@bot.command(name='debugadv')
@is_sub_moderator_or_higher()
async def debug_adv_command(ctx):
    """Comando de debug para verificar advertências"""
    
    # Verificar cargos
    cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
    cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID) 
    cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
    
    debug_text = f"🔍 **DEBUG DE ADVERTÊNCIAS**\n\n"
    debug_text += f"**CARGOS ADV:**\n"
    debug_text += f"🟡 ADV 1 (ID: {ADV_CARGO_1_ID}): {cargo_adv1.name if cargo_adv1 else '❌ NÃO ENCONTRADO'}\n"
    debug_text += f"🟠 ADV 2 (ID: {ADV_CARGO_2_ID}): {cargo_adv2.name if cargo_adv2 else '❌ NÃO ENCONTRADO'}\n"
    debug_text += f"🔴 ADV 3 (ID: {ADV_CARGO_3_ID}): {cargo_adv3.name if cargo_adv3 else '❌ NÃO ENCONTRADO'}\n\n"
    
    # Verificar usuários com cargos
    users_with_adv = []
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        has_adv1 = cargo_adv1 and cargo_adv1 in member.roles
        has_adv2 = cargo_adv2 and cargo_adv2 in member.roles  
        has_adv3 = cargo_adv3 and cargo_adv3 in member.roles
        
        if has_adv1 or has_adv2 or has_adv3:
            roles = []
            if has_adv1: roles.append("ADV1")
            if has_adv2: roles.append("ADV2") 
            if has_adv3: roles.append("ADV3")
            users_with_adv.append(f"• {member.display_name}: {', '.join(roles)}")
    
    debug_text += f"**USUÁRIOS COM CARGOS ADV:** {len(users_with_adv)}\n"
    if users_with_adv:
        debug_text += "\n".join(users_with_adv)  # TODOS os usuários
    else:
        debug_text += "Nenhum usuário encontrado com cargos ADV"
    
    debug_text += f"\n\n**DADOS SALVOS:** {len(user_warnings)} usuários\n"
    for user_id, warnings in user_warnings.items():  # TODOS os dados salvos
        if warnings > 0:
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"ID:{user_id}"
            debug_text += f"• {name}: {warnings} advertências\n"
    
    embed = discord.Embed(
        title="🔍 DEBUG DE ADVERTÊNCIAS",
        description=debug_text[:2000],
        color=0x00ffff
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='mute')
@is_sub_moderator_or_higher()
async def mute_command(ctx, usuario: discord.Member = None, *, args=None):
    """Muta usuário com tempo opcional - Uso: .mute @usuário motivo tempo"""
    
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!",
            color=0xff0000
        )
        embed.add_field(
            name="📝 Uso Correto",
            value="`.mute @usuário [motivo] [tempo]`",
            inline=False
        )
        embed.add_field(
            name="📝 Exemplos",
            value="`.mute @João spam` (indefinido)\n`.mute @João flood 1h` (1 hora)\n`.mute @João toxic 30m` (30 minutos)\n`.mute @João raid 2d` (2 dias)",
            inline=False
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se mutar!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode mutar este usuário!")
        return
    
    # Processar argumentos (motivo e tempo)
    motivo = "Sem motivo especificado"
    duracao_texto = "Indefinido"
    duracao_minutos = None
    
    if args:
        import re
        # Procurar padrão de tempo (1h, 30m, 2d, etc)
        tempo_match = re.search(r'(\d+)([smhd])', args.lower())
        
        if tempo_match:
            numero = int(tempo_match.group(1))
            unidade = tempo_match.group(2)
            
            # Converter para minutos
            if unidade == 's':  # segundos
                duracao_minutos = numero // 60 if numero >= 60 else 1
                duracao_texto = f"{numero} segundos"
            elif unidade == 'm':  # minutos
                duracao_minutos = numero
                duracao_texto = f"{numero} minutos"
            elif unidade == 'h':  # horas
                duracao_minutos = numero * 60
                duracao_texto = f"{numero} horas"
            elif unidade == 'd':  # dias
                duracao_minutos = numero * 1440
                duracao_texto = f"{numero} dias"
            
            # Limitar a 28 dias (limite do Discord)
            if duracao_minutos > 40320:
                duracao_minutos = 40320
                duracao_texto = "28 dias (máximo)"
            
            # Remover tempo do motivo
            motivo = args.replace(tempo_match.group(0), '').strip()
        else:
            motivo = args
        
        if not motivo:
            motivo = "Sem motivo especificado"
    
    try:
        # Obter ou criar cargo de mute
        mute_role = await get_or_create_mute_role(ctx.guild)
        if not mute_role:
            await ctx.reply("❌ Erro ao criar cargo de mute!")
            return
        
        # Verificar se já está mutado
        if mute_role in usuario.roles:
            await ctx.reply("❌ Este usuário já está mutado!")
            return
        
        # Aplicar mute
        await usuario.add_roles(mute_role, reason=f"Mutado por {ctx.author} | Motivo: {motivo} | Duração: {duracao_texto}")
        
        # Se tem duração, agendar unmute
        if duracao_minutos:
            asyncio.create_task(auto_unmute(usuario, mute_role, duracao_minutos))
        
        embed = discord.Embed(
            title="🔇 USUÁRIO MUTADO",
            description=f"**{usuario.display_name}** foi mutado com sucesso!",
            color=0x808080
        )
        embed.add_field(
            name="📝 Motivo",
            value=f"`{motivo}`",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.add_field(
            name="⏰ Duração",
            value=duracao_texto,
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
    except discord.Forbidden:
        pass
    except Exception as e:
        await ctx.reply(f"❌ Erro ao mutar usuário: {e}")

async def auto_unmute(usuario, mute_role, minutos):
    """Remove mute automaticamente após o tempo"""
    import asyncio
    await asyncio.sleep(minutos * 60)
    try:
        if mute_role in usuario.roles:
            await usuario.remove_roles(mute_role, reason="Tempo de mute expirado")
    except:
        pass

@mute_command.error
async def mute_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='unmute')
@is_sub_moderator_or_higher()
async def unmute_command(ctx, usuario: discord.Member = None):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `.unmute @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    try:
        # Obter cargo de mute
        mute_role = await get_or_create_mute_role(ctx.guild)
        if not mute_role:
            await ctx.reply("❌ Erro ao encontrar/criar cargo de mute!")
            return
        
        # Verificar se está mutado (buscar por qualquer cargo de mute possível)
        user_mute_roles = []
        common_mute_names = ["Muted", "Mutado", "Silenciado", "Mute"]
        
        for role in usuario.roles:
            if role.name in common_mute_names or role == mute_role:
                user_mute_roles.append(role)
        
        if not user_mute_roles:
            await ctx.reply("❌ Este usuário não está mutado!")
            return
        
        # Remover todos os cargos de mute encontrados
        for mute_role_to_remove in user_mute_roles:
            try:
                await usuario.remove_roles(mute_role_to_remove, reason=f"Desmutado por {ctx.author}")
            except Exception as e:
                print(f"Erro ao remover cargo {mute_role_to_remove.name}: {e}")
                continue
        
        embed = discord.Embed(
            title="🔊 MUTE REMOVIDO",
            description=f"**{usuario.display_name}** pode falar novamente!",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
    except discord.Forbidden:
        pass  # Não mostrar erro se a ação foi executada
    except Exception as e:
        await ctx.reply(f"❌ Erro ao desmutar usuário: {e}")

@unmute_command.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

# COMANDO RADVALLSERVER REMOVIDO - CONFORME SOLICITADO

# ========================================
# COMANDOS BÁSICOS DE MODERAÇÃO
# ========================================

@bot.command(name='kick')
@is_sub_moderator_or_higher()
async def kick_command(ctx, usuario: discord.Member = None, *, motivo="Sem motivo especificado"):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!kick @usuário [motivo]`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se expulsar!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode expulsar este usuário!")
        return
    
    try:
        # Salvar informações antes de kickar
        user_name = usuario.name
        user_id = usuario.id
        user_avatar = usuario.display_avatar.url
        user_created_at = usuario.created_at
        user_joined_at = usuario.joined_at
        
        # Mensagem de confirmação no canal
        embed = discord.Embed(
            title="👢 USUÁRIO EXPULSO",
            description=f"**{usuario.display_name}** foi expulso do servidor!",
            color=0xff8c00
        )
        embed.add_field(
            name="📝 Motivo",
            value=f"`{motivo}`",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=f"{usuario.mention}\n`{usuario.id}`",
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
        # Executar kick
        await usuario.kick(reason=f"Expulso por {ctx.author} | Motivo: {motivo}")
        
        # LOG DETALHADA DE KICK
        log_channel = ctx.guild.get_channel(KICK_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="👢 USUÁRIO EXPULSO (KICK)",
                description=f"Um membro foi expulso do servidor",
                color=0xFFA500,  # LARANJA
                timestamp=datetime.now()
            )
            
            log_embed.add_field(
                name="👤 Usuário Expulso",
                value=f"**Nome:** {user_name}\n**ID:** `{user_id}`",
                inline=True
            )
            
            log_embed.add_field(
                name="👮 Moderador",
                value=f"**Nome:** {ctx.author.name}\n**Tag:** {ctx.author.mention}\n**ID:** `{ctx.author.id}`",
                inline=True
            )
            
            log_embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            log_embed.add_field(
                name="📝 Motivo",
                value=f"```{motivo}```",
                inline=False
            )
            
            log_embed.add_field(
                name="📊 Informações do Usuário",
                value=f"**Conta criada em:** <t:{int(user_created_at.timestamp())}:F>\n**Entrou no servidor em:** <t:{int(user_joined_at.timestamp())}:F>\n**Tempo no servidor:** {(datetime.now() - user_joined_at.replace(tzinfo=None)).days} dias",
                inline=False
            )
            
            log_embed.add_field(
                name="📍 Canal da Ação",
                value=f"{ctx.channel.mention} (`{ctx.channel.name}`)",
                inline=False
            )
            
            log_embed.set_thumbnail(url=user_avatar)
            log_embed.set_footer(text=f"Sistema de Logs • Kick ID: {user_id}")
            
            await log_channel.send(embed=log_embed)
            print(f"📋 Log de kick registrado para {user_name}")
        
    except discord.Forbidden:
        pass  # Não mostrar erro se a ação foi executada
    except Exception as e:
        await ctx.reply(f"❌ Erro ao expulsar usuário: {e}")

@kick_command.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='ban')
@is_sub_moderator_or_higher()
async def ban_command(ctx, usuario: discord.Member = None, *, motivo="Sem motivo especificado"):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!ban @usuário [motivo]`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se banir!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode banir este usuário!")
        return
    
    try:
        embed = discord.Embed(
            title="🔨 USUÁRIO BANIDO",
            description=f"**{usuario.display_name}** foi banido do servidor!",
            color=0xff0000
        )
        embed.add_field(
            name="📝 Motivo",
            value=f"`{motivo}`",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=f"{usuario.mention}\n`{usuario.id}`",
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
        await usuario.ban(reason=f"Banido por {ctx.author} | Motivo: {motivo}")
        
    except discord.Forbidden:
        pass  # Não mostrar erro se a ação foi executada
    except Exception as e:
        await ctx.reply(f"❌ Erro ao banir usuário: {e}")

@ban_command.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='timeout')
@is_sub_moderator_or_higher()
async def timeout_command(ctx, usuario: discord.Member = None, *, args=None):
    """Aplica timeout com tempo - Uso: .timeout @usuário motivo tempo"""
    
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!",
            color=0xff0000
        )
        embed.add_field(
            name="📝 Uso Correto",
            value="`.timeout @usuário [motivo] [tempo]`",
            inline=False
        )
        embed.add_field(
            name="📝 Exemplos",
            value="`.timeout @João spam 10m` (10 minutos)\n`.timeout @João flood 1h` (1 hora)\n`.timeout @João toxic 30m` (30 minutos)\n`.timeout @João raid 2d` (2 dias)",
            inline=False
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se silenciar!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode silenciar este usuário!")
        return
    
    # Verificar se já está em timeout
    if usuario.timed_out_until and usuario.timed_out_until > discord.utils.utcnow():
        await ctx.reply("❌ Este usuário já está em timeout!")
        return
    
    # Processar argumentos (motivo e tempo)
    motivo = "Sem motivo especificado"
    duracao_texto = "10 minutos"
    duracao_minutos = 10  # Padrão
    
    if args:
        import re
        # Procurar padrão de tempo (1h, 30m, 2d, etc)
        tempo_match = re.search(r'(\d+)([smhd])', args.lower())
        
        if tempo_match:
            numero = int(tempo_match.group(1))
            unidade = tempo_match.group(2)
            
            # Converter para minutos
            if unidade == 's':  # segundos
                duracao_minutos = numero // 60 if numero >= 60 else 1
                duracao_texto = f"{numero} segundos"
            elif unidade == 'm':  # minutos
                duracao_minutos = numero
                duracao_texto = f"{numero} minutos"
            elif unidade == 'h':  # horas
                duracao_minutos = numero * 60
                duracao_texto = f"{numero} horas"
            elif unidade == 'd':  # dias
                duracao_minutos = numero * 1440
                duracao_texto = f"{numero} dias"
            
            # Limitar a 28 dias (limite do Discord)
            if duracao_minutos > 40320:
                duracao_minutos = 40320
                duracao_texto = "28 dias (máximo)"
            
            # Remover tempo do motivo
            motivo = args.replace(tempo_match.group(0), '').strip()
        else:
            motivo = args
        
        if not motivo:
            motivo = "Sem motivo especificado"
    
    try:
        # Calcular duração do timeout (CORRIGIDO - usar datetime.timedelta)
        from datetime import timedelta
        timeout_duration = discord.utils.utcnow() + timedelta(minutes=duracao_minutos)
        
        # Aplicar timeout
        await usuario.timeout(timeout_duration, reason=f"Timeout por {ctx.author.display_name} | Motivo: {motivo}")
        
        embed = discord.Embed(
            title="🔇 USUÁRIO EM TIMEOUT",
            description=f"**{usuario.display_name}** foi silenciado com sucesso!",
            color=0xffa500
        )
        embed.add_field(
            name="📝 Motivo",
            value=f"`{motivo}`",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.add_field(
            name="⏰ Duração",
            value=duracao_texto,
            inline=True
        )
        embed.add_field(
            name="📅 Expira em",
            value=f"<t:{int(timeout_duration.timestamp())}:F>",
            inline=False
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para aplicar timeout neste usuário!")
    except discord.HTTPException as e:
        await ctx.reply(f"❌ Erro do Discord ao aplicar timeout: {e}")
    except Exception as e:
        await ctx.reply(f"❌ Erro inesperado ao silenciar usuário: {e}")

@timeout_command.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='untimeout')
@is_sub_moderator_or_higher()
async def untimeout_command(ctx, usuario: discord.Member = None):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!untimeout @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    try:
        if usuario.timed_out_until is None:
            await ctx.reply("❌ Este usuário não está silenciado!")
            return
        
        embed = discord.Embed(
            title="🔊 SILENCIAMENTO REMOVIDO",
            description=f"**{usuario.display_name}** pode falar novamente!",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 Usuário",
            value=usuario.mention,
            inline=True
        )
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
        await usuario.timeout(None, reason=f"Timeout removido por {ctx.author}")
        
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para remover timeout!")
    except Exception as e:
        await ctx.reply(f"❌ Erro ao remover timeout: {e}")

@untimeout_command.error
async def untimeout_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='clear')
@is_sub_moderator_or_higher()
async def clear_command(ctx, quantidade: int = 10):
    if quantidade > 100:
        quantidade = 100
    elif quantidade < 1:
        quantidade = 1
    
    try:
        deleted = await ctx.channel.purge(limit=quantidade + 1)  # +1 para incluir o comando
        
        embed = discord.Embed(
            title="🧹 MENSAGENS LIMPAS",
            description=f"**{len(deleted) - 1}** mensagens foram deletadas!",
            color=0x00ff00
        )
        embed.add_field(
            name="📊 Detalhes",
            value=f"**Canal:** {ctx.channel.mention}\n**Moderador:** {ctx.author.mention}",
            inline=False
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
        
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para deletar mensagens!")
    except Exception as e:
        await ctx.reply(f"❌ Erro ao limpar mensagens: {e}")

@clear_command.error
async def clear_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

@bot.command(name='restart')
@commands.has_permissions(administrator=True)
async def restart_command(ctx):
    """Reinicia o bot para resolver problemas de duplicação"""
    embed = discord.Embed(
        title="🔄 REINICIANDO BOT",
        description="O bot será reiniciado em 3 segundos...",
        color=0xffaa00
    )
    embed.add_field(
        name="⚠️ Atenção",
        value="Isso vai resolver problemas de:\n• Mensagens duplicadas\n• Comandos travados\n• Cache corrompido",
        inline=False
    )
    embed.set_footer(text="Sistema de Manutenção • Caos Hub")
    await ctx.reply(embed=embed)
    
    await asyncio.sleep(3)
    
    # Salvar dados antes de reiniciar
    save_warnings_data()
    save_role_config()
    
    # Reiniciar o bot
    await bot.close()
    
    # No Render, o bot reinicia automaticamente após fechar
    import sys
    import os
    os.execv(sys.executable, ['python'] + sys.argv)

@restart_command.error
async def restart_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para reiniciar o bot!")


# ========================================
# COMANDO .SCAN - PEGAR TODOS OS IDS DO SERVIDOR
# ========================================
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




# ========================================
# SISTEMA ANTI-SPAM - VERSÃO FINAL
# ========================================

async def auto_moderate_spam(message, violation_type, details=""):
    """Sistema anti-spam: 5 msgs = aviso 1, 4 msgs = aviso 2, 3 msgs = ADV + TIMEOUT"""
    user_id = message.author.id
    
    # Deletar mensagem
    try:
        await message.delete()
    except:
        pass
    
    # Incrementar contador
    if user_id not in spam_warnings:
        spam_warnings[user_id] = 0
    spam_warnings[user_id] += 1
    count = spam_warnings[user_id]
    
    # PRIMEIRO AVISO - EXATAMENTE 5 mensagens
    if count == 5:
        embed = discord.Embed(
            title="⚠️ PRIMEIRO AVISO - SPAM DETECTADO",
            description=f"**{message.author.display_name}**, você foi detectado fazendo spam!",
            color=0xffff00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Próximo:** Segundo aviso (4 mensagens)",
            inline=False
        )
        embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
        await message.channel.send(embed=embed)
        # NÃO RESETAR - continua contando
        
    # SEGUNDO AVISO - 9 mensagens (5 + 4)
    elif count == 9:
        embed = discord.Embed(
            title="🚨 SEGUNDO AVISO - ÚLTIMA CHANCE",
            description=f"**{message.author.display_name}**, PARE DE FAZER SPAM!",
            color=0xff8c00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Próximo:** ADV 1 + Timeout (3 mensagens)",
            inline=False
        )
        embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
        await message.channel.send(embed=embed)
        # NÃO RESETAR - continua contando
        
    # ADV - 12 mensagens (5 + 4 + 3)
    elif count >= 12:
        # Verificar quantas ADVs o usuário já tem (SEM incrementar ainda)
        if user_id not in user_warnings:
            user_warnings[user_id] = 0
        
        # Verificar qual ADV vai receber BASEADO no que já tem
        current_adv = user_warnings[user_id]
        
        # Incrementar APENAS quando aplicar ADV
        user_warnings[user_id] += 1
        adv_count = user_warnings[user_id]
        
        # ADV 1 (usuário não tinha ADV)
        if adv_count == 1:
            cargo = message.guild.get_role(ADV_CARGO_1_ID)
            adv_level = "ADV 1"
            color = 0xffff00
            next_adv = "ADV 2"
            
        # ADV 2
        elif adv_count == 2:
            # Remover ADV 1
            cargo_adv1 = message.guild.get_role(ADV_CARGO_1_ID)
            if cargo_adv1 and cargo_adv1 in message.author.roles:
                await message.author.remove_roles(cargo_adv1)
            
            cargo = message.guild.get_role(ADV_CARGO_2_ID)
            adv_level = "ADV 2"
            color = 0xff8c00
            next_adv = "ADV 3 + BAN"
            
        # ADV 3 = BAN IMEDIATO
        else:
            # Remover ADV 1 e 2
            cargo_adv1 = message.guild.get_role(ADV_CARGO_1_ID)
            cargo_adv2 = message.guild.get_role(ADV_CARGO_2_ID)
            if cargo_adv1 and cargo_adv1 in message.author.roles:
                await message.author.remove_roles(cargo_adv1)
            if cargo_adv2 and cargo_adv2 in message.author.roles:
                await message.author.remove_roles(cargo_adv2)
            
            cargo = message.guild.get_role(ADV_CARGO_3_ID)
            if cargo:
                await message.author.add_roles(cargo)
            
            # BANIR IMEDIATAMENTE
            embed = discord.Embed(
                title="🔨 ADV 3 - BANIMENTO AUTOMÁTICO",
                description=f"**{message.author.display_name}** foi banido por atingir ADV 3!",
                color=0xff0000
            )
            embed.add_field(
                name="📋 Motivo",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}",
                inline=False
            )
            embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
            await message.channel.send(embed=embed)
            
            await message.author.ban(reason="ADV 3 - Spam repetido")
            user_warnings[user_id] = 0
            spam_warnings[user_id] = 0
            save_warnings_data()
            return
        
        # Aplicar cargo ADV
        if cargo:
            await message.author.add_roles(cargo)
        
        # APLICAR TIMEOUT DE 1 MINUTO - IGUAL AO COMANDO .timeout
        from datetime import timedelta
        timeout_aplicado = False
        try:
            timeout_duration = discord.utils.utcnow() + timedelta(minutes=1)
            await message.author.timeout(timeout_duration, reason=f"{adv_level} - Spam automático")
            timeout_aplicado = True
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass
        except Exception:
            pass
        
        # Embed de ADV aplicada COM TIMEOUT
        embed = discord.Embed(
            title=f"🚨 {adv_level} APLICADA",
            description=f"**{message.author.display_name}** recebeu {adv_level} por spam!",
            color=color
        )
        embed.add_field(
            name="📝 Motivo",
            value=f"`{violation_type}`",
            inline=False
        )
        embed.add_field(
            name="👤 Usuário",
            value=message.author.mention,
            inline=True
        )
        embed.add_field(
            name="⏰ Timeout",
            value="1 minuto" if timeout_aplicado else "❌ Falhou",
            inline=True
        )
        embed.add_field(
            name="🚨 Próxima Punição",
            value=next_adv,
            inline=True
        )
        if timeout_aplicado:
            embed.add_field(
                name="📅 Expira em",
                value=f"<t:{int((discord.utils.utcnow() + timedelta(minutes=1)).timestamp())}:F>",
                inline=False
            )
        embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
        await message.channel.send(embed=embed)
        
        # RESETAR contador de spam (volta pro zero - precisa fazer 5→9→12 de novo)
        spam_warnings[user_id] = 0
        save_warnings_data()

# ========================================
# SISTEMA DE AJUDA PERSONALIZADO
# ========================================

# Remover comando help padrão
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx, categoria=None):
    """Sistema de ajuda personalizado com categorias"""
    
    if categoria is None:
        # Menu principal de categorias
        embed = discord.Embed(
            title="🤖 CENTRAL DE AJUDA - CAOS BOT",
            description="**Bem-vindo ao sistema de ajuda!** 🎉\n\nEscolha uma categoria abaixo para ver os comandos disponíveis:",
            color=0x00ff88
        )
        
        embed.add_field(
            name="🛡️ **MODERAÇÃO**",
            value="`.help moderacao`\nComandos para moderar o servidor",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ **ADVERTÊNCIAS**",
            value="`.help advertencias`\nSistema de advertências progressivas",
            inline=True
        )
        
        embed.add_field(
            name="🔇 **MUTE & TIMEOUT**",
            value="`.help mute`\nComandos de silenciamento",
            inline=True
        )
        
        embed.add_field(
            name="🎮 **DIVERSÃO**",
            value="`.help diversao`\nComandos para se divertir",
            inline=True
        )
        
        embed.add_field(
            name="💬 **CONVERSA**",
            value="`.help conversa`\nComandos de interação social",
            inline=True
        )
        
        embed.add_field(
            name="🛠️ **UTILIDADES**",
            value="`.help utilidades`\nComandos úteis diversos",
            inline=True
        )
        
        embed.add_field(
            name="📊 **INFORMAÇÕES**",
            value="**Prefixo:** `.` (ponto)\n**Permissões:** Sub Moderador+\n**Versão:** 2.0 Premium",
            inline=False
        )
        
        embed.set_footer(text="💡 Dica: Use .help [categoria] para ver comandos específicos • Caos Hub")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
        await ctx.reply(embed=embed)
        return
    
    # Categorias específicas
    categoria = categoria.lower()
    
    if categoria in ['moderacao', 'moderação', 'mod']:
        embed = discord.Embed(
            title="🛡️ COMANDOS DE MODERAÇÃO",
            description="**Comandos para manter a ordem no servidor**\n*Requer: Sub Moderador ou permissões de moderação*",
            color=0xff4444
        )
        
        embed.add_field(
            name="👢 `.kick @usuário [motivo]`",
            value="**Expulsa** um usuário do servidor\n*Exemplo: `.kick @João spam`*",
            inline=False
        )
        
        embed.add_field(
            name="🔨 `.ban @usuário [motivo]`",
            value="**Bane** um usuário permanentemente\n*Exemplo: `.ban @João comportamento tóxico`*",
            inline=False
        )
        
        embed.add_field(
            name="🔇 `.timeout @usuário [minutos] [motivo]`",
            value="**Silencia** temporariamente (máx 24h)\n*Exemplo: `.timeout @João 30 flood`*",
            inline=False
        )
        
        embed.add_field(
            name="🔊 `.untimeout @usuário`",
            value="**Remove** o timeout de um usuário\n*Exemplo: `.untimeout @João`*",
            inline=False
        )
        
        embed.add_field(
            name="🧹 `.clear [quantidade]`",
            value="**Deleta** mensagens (1-100, padrão: 10)\n*Exemplo: `.clear 50`*",
            inline=False
        )
        
        embed.add_field(
            name="🎯 `.addrole @cargo @usuário`",
            value="**Adiciona** cargo ao usuário e aplica prefixo\n*Exemplo: `.addrole @Moderador @João`*",
            inline=False
        )
        
        embed.add_field(
            name="🗑️ `.removerole @cargo @usuário`",
            value="**Remove** cargo do usuário e restaura nickname\n*Exemplo: `.removerole @Moderador @João`*",
            inline=False
        )
        
        embed.set_footer(text="🛡️ Moderação • Use com responsabilidade")
        
    elif categoria in ['advertencias', 'advertências', 'adv']:
        embed = discord.Embed(
            title="⚠️ SISTEMA DE ADVERTÊNCIAS",
            description="**Sistema progressivo de punições**\n*ADV 1 → ADV 2 → ADV 3 + Ban Automático*",
            color=0xffaa00
        )
        
        embed.add_field(
            name="⚠️ `.adv @usuário [motivo]`",
            value="**Aplica** advertência progressiva\n*Exemplo: `.adv @João linguagem inadequada`*",
            inline=False
        )
        
        embed.add_field(
            name="🔄 `.radv @usuário`",
            value="**Remove** UMA advertência por vez\n*Exemplo: `.radv @João`*",
            inline=False
        )
        
        embed.add_field(
            name="🧹 `.radvall @usuário`",
            value="**Remove** TODAS as advertências\n*Exemplo: `.radvall @João`*",
            inline=False
        )
        
        
        embed.add_field(
            name="📋 **NÍVEIS DE ADVERTÊNCIA**",
            value="🟡 **ADV 1** - Primeira advertência\n🟠 **ADV 2** - Segunda advertência\n🔴 **ADV 3** - Terceira + Ban automático",
            inline=False
        )
        
        embed.set_footer(text="⚠️ Advertências • Sistema automático de punições")
        
    elif categoria in ['mute', 'timeout', 'silenciar']:
        embed = discord.Embed(
            title="🔇 COMANDOS DE SILENCIAMENTO",
            description="**Controle total sobre comunicação dos usuários**",
            color=0x808080
        )
        
        embed.add_field(
            name="🔇 `.mute @usuário [motivo]`",
            value="**Muta** usuário indefinidamente\n*Remove capacidade de falar/reagir*\n*Exemplo: `.mute @João comportamento inadequado`*",
            inline=False
        )
        
        embed.add_field(
            name="🔊 `.unmute @usuário`",
            value="**Desmuta** usuário mutado\n*Restaura capacidade de comunicação*\n*Exemplo: `.unmute @João`*",
            inline=False
        )
        
        embed.add_field(
            name="⏰ `.timeout @usuário [minutos] [motivo]`",
            value="**Timeout** temporário (1-1440 min)\n*Silenciamento com duração definida*\n*Exemplo: `.timeout @João 60 spam`*",
            inline=False
        )
        
        embed.add_field(
            name="⏰ `.untimeout @usuário`",
            value="**Remove** timeout ativo\n*Cancela silenciamento temporário*\n*Exemplo: `.untimeout @João`*",
            inline=False
        )
        
        embed.add_field(
            name="🔍 **DIFERENÇAS**",
            value="**Mute:** Indefinido, manual para remover\n**Timeout:** Temporário, remove automaticamente",
            inline=False
        )
        
        embed.set_footer(text="🔇 Silenciamento • Mute vs Timeout")
        
    elif categoria in ['diversao', 'diversão', 'fun']:
        embed = discord.Embed(
            title="🎮 COMANDOS DE DIVERSÃO",
            description="**Comandos para animar o servidor e se divertir!**",
            color=0xff69b4
        )
        
        embed.add_field(
            name="😂 `.piada`",
            value="**Conta** uma piada aleatória\n*Humor garantido!*",
            inline=True
        )
        
        embed.add_field(
            name="🎲 `.escolher opção1, opção2, ...`",
            value="**Escolhe** entre várias opções\n*Exemplo: `.escolher pizza, hambúrguer, sushi`*",
            inline=True
        )
        
        embed.add_field(
            name="🎯 **MAIS COMANDOS**",
            value="*Mais comandos de diversão em breve!*\n*Sugestões são bem-vindas*",
            inline=False
        )
        
        embed.set_footer(text="🎮 Diversão • Mais comandos em desenvolvimento")
        
    elif categoria in ['conversa', 'social', 'chat']:
        embed = discord.Embed(
            title="💬 COMANDOS DE CONVERSA",
            description="**Comandos para interação social e conversas**",
            color=0x87ceeb
        )
        
        embed.add_field(
            name="👋 `.oi`",
            value="**Cumprimenta** com saudações aleatórias\n*Inicia conversas de forma amigável*",
            inline=True
        )
        
        embed.add_field(
            name="🤗 `.comoesta [@usuário]`",
            value="**Pergunta** como alguém está\n*Demonstra interesse genuíno*",
            inline=True
        )
        
        embed.add_field(
            name="💭 `.conversa`",
            value="**Sugere** tópicos de conversa\n*Quebra o gelo em conversas*",
            inline=True
        )
        
        embed.add_field(
            name="🌤️ `.clima`",
            value="**Pergunta** sobre humor/energia\n*Conecta com o estado emocional*",
            inline=True
        )
        
        embed.add_field(
            name="👋 `.tchau`",
            value="**Despede-se** com mensagens carinhosas\n*Finaliza conversas educadamente*",
            inline=True
        )
        
        embed.add_field(
            name="🤗 `.abraco [@usuário]`",
            value="**Envia** abraços virtuais\n*Demonstra carinho e apoio*",
            inline=True
        )
        
        embed.add_field(
            name="✨ `.elogio [@usuário]`",
            value="**Faz** elogios motivacionais\n*Eleva a autoestima dos outros*",
            inline=True
        )
        
        embed.add_field(
            name="💪 `.motivacao`",
            value="**Compartilha** frases inspiradoras\n*Motiva e inspira positivamente*",
            inline=True
        )
        
        embed.set_footer(text="💬 Conversa • Interações sociais saudáveis")
        
    elif categoria in ['utilidades', 'utils', 'uteis']:
        embed = discord.Embed(
            title="🛠️ COMANDOS UTILITÁRIOS",
            description="**Comandos úteis para administração e informações**",
            color=0x9932cc
        )
        
        
        embed.add_field(
            name="🧹 `.clear [quantidade]`",
            value="**Limpa** mensagens do canal\n*Organização e limpeza*",
            inline=False
        )
        
        embed.add_field(
            name="❓ `.help [categoria]`",
            value="**Mostra** esta ajuda\n*Sistema de ajuda completo*",
            inline=False
        )
        
        
        
        embed.add_field(
            name="🔧 **EM DESENVOLVIMENTO**",
            value="*Mais utilitários sendo desenvolvidos*\n*Sugestões são bem-vindas*",
            inline=False
        )
        
        embed.set_footer(text="🛠️ Utilidades • Ferramentas administrativas")
        
    else:
        embed = discord.Embed(
            title="❌ CATEGORIA NÃO ENCONTRADA",
            description="**Categoria inválida!** Use uma das opções abaixo:",
            color=0xff0000
        )
        
        embed.add_field(
            name="📋 **CATEGORIAS DISPONÍVEIS**",
            value="• `moderacao` - Comandos de moderação\n• `advertencias` - Sistema de advertências\n• `mute` - Comandos de silenciamento\n• `diversao` - Comandos de diversão\n• `conversa` - Comandos sociais\n• `utilidades` - Comandos utilitários",
            inline=False
        )
        
        embed.add_field(
            name="💡 **EXEMPLO**",
            value="`.help moderacao` - Ver comandos de moderação",
            inline=False
        )
        
        embed.set_footer(text="❌ Erro • Use .help para ver o menu principal")
    
    await ctx.reply(embed=embed)

# ========================================
# COMANDOS DE DIVERSÃO
# ========================================

@bot.command(name='piada')
async def piada_command(ctx):
    piadas = [
        'Por que os pássaros voam para o sul no inverno? Porque é longe demais para ir andando! 🐦',
        'O que o pato disse para a pata? Vem quá! 🦆',
        'Por que o livro de matemática estava triste? Porque tinha muitos problemas! 📚',
        'O que a impressora falou para a outra impressora? Essa folha é sua ou é impressão minha? 🖨️',
        'Por que o café foi para a polícia? Porque foi roubado! ☕',
        'O que o oceano disse para a praia? Nada, só acenou! 🌊',
        'Por que os esqueletos não brigam? Porque não têm estômago para isso! 💀',
        'O que a fechadura disse para a chave? Você é a chave do meu coração! 🔐'
    ]
    piada = random.choice(piadas)
    
    embed = discord.Embed(
        title="😄 Piada do Dia",
        description=piada,
        color=0xffff00
    )
    embed.set_footer(text="Comandos de Diversão • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='escolher')
async def escolher_command(ctx, *, opcoes):
    lista_opcoes = [opcao.strip() for opcao in opcoes.split(',')]
    if len(lista_opcoes) < 2:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description='Preciso de pelo menos 2 opções separadas por vírgula!',
            color=0xff0000
        )
        embed.add_field(
            name="📝 Exemplo",
            value="`.escolher pizza, hambúrguer, sushi`",
            inline=False
        )
        embed.set_footer(text="Comandos de Diversão • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    escolha = random.choice(lista_opcoes)
    
    embed = discord.Embed(
        title="🎲 Escolha Aleatória",
        description=f'Eu escolho: **{escolha}**!',
        color=0x9932cc
    )
    embed.add_field(
        name="📋 Opções Disponíveis",
        value=", ".join(lista_opcoes),
        inline=False
    )
    embed.set_footer(text="Comandos de Diversão • Caos Hub")
    await ctx.reply(embed=embed)

@bot.command(name='embedhub')
@commands.has_permissions(administrator=True)
async def embedhub_command(ctx):
    """Envia o embed FODA do Caos Hub com TODOS os GIFs"""
    
    # EMBED ÚNICO COM TUDO
    embed = discord.Embed(
        title="🔥 BEM-VINDO AO CAOS HUB! 🔥",
        description=(
            "# **O MELHOR HUB DE SCRIPTS DO BRASIL!**\n\n"
            "Aqui você encontra **TUDO** que precisa para dominar seus jogos favoritos!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xff6600
    )
    
    # GIF PRINCIPAL
    embed.set_image(url="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHpuMWV1eWprbm1vZGgzZnlseWJ6ZWxjbmsxbG5yczhta2FnNzQ1ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Q8gqp0zwvSoMaDX1uS/giphy.gif")
    
    # THUMBNAIL
    embed.set_thumbnail(url="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmV0Zm1nbmJocDhweDNvbDRreGZhOG5rcmZvenN5Nmw1Z3N2aWxtayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/10TZs8ho7qJeVy/giphy.gif")
    
    embed.add_field(
        name="🎯 O QUE OFERECEMOS",
        value=(
            "🔹 **Scripts Premium** - Os melhores do mercado\n"
            "🔹 **Executores Confiáveis** - Testados e aprovados\n"
            "🔹 **Suporte 24/7** - Equipe sempre disponível\n"
            "🔹 **Atualizações Constantes** - Sempre atualizado\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎫 COMO ACESSAR",
        value=(
            "**1.** Acesse o canal <#1417548428984188929>\n"
            "**2.** Abra um ticket clicando no botão\n"
            "**3.** Escolha a categoria desejada\n"
            "**4.** Nossa equipe responderá rapidamente!"
        ),
        inline=True
    )
    
    embed.add_field(
        name="⚙️ EXECUTORES ACEITOS",
        value=(
            "✅ **Synapse X**\n"
            "✅ **Script-Ware**\n"
            "✅ **KRNL**\n"
            "✅ **Fluxus**\n"
            "✅ **Arceus X**\n"
            "✅ **E muito mais!**"
        ),
        inline=True
    )
    
    embed.add_field(
        name="🎮 JOGOS DISPONÍVEIS",
        value="🥊 **The Strongest Battlegrounds**",
        inline=False
    )
    
    embed.add_field(
        name="💳 FORMAS DE PAGAMENTO",
        value=(
            "💰 **PIX** - Instantâneo e seguro\n"
            "💵 **PayPal** - Internacional\n\n"
            "🎮 **Robux** - Em breve!"
        ),
        inline=False
    )
    
    embed.set_footer(
        text="🔥 CAOS Hub © 2025 • Todos os direitos reservados • Melhor Hub de Scripts!",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    
    embed.timestamp = discord.utils.utcnow()
    
    # ENVIAR COM @everyone
    await ctx.send("@everyone", embed=embed)
    
    try:
        await ctx.message.delete()
    except:
        pass

@embedhub_command.error
async def embedhub_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

# ========================================
# RESPOSTAS AUTOMÁTICAS E PROTEÇÕES
# ========================================

@bot.event
async def on_message_old(message):
    # FUNÇÃO ANTIGA - NÃO USAR (mantida para referência)
    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return
    
    # Ignorar moderadores (usuários com permissão de gerenciar mensagens)
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return
    
    user_id = message.author.id
    current_time = time.time()
    content = message.content
    
    # ========================================
    # SISTEMA ANTI-MENÇÃO (MÁXIMO 1 MENÇÃO) - VERIFICAR PRIMEIRO
    # ========================================
    
    # Verificar menções (permitido apenas 1, se tiver 2 ou mais já avisa)
    mention_count = len(message.raw_mentions) + len(message.raw_role_mentions)
    print(f"[DEBUG MENÇÃO] Usuário: {message.author} | Menções: {mention_count}")  # DEBUG
    
    if mention_count >= 2:  # agora dispara com 2 ou mais
        try:
            await message.delete()
        except:
            pass
        
        # Criar lista de menções (com repetições preservadas)
        mencoes = []
        for uid in message.raw_mentions:
            mencoes.append(f"<@{uid}>")
        for rid in message.raw_role_mentions:
            mencoes.append(f"<@&{rid}>")
        
        embed = discord.Embed(
            title="⚠️ EXCESSO DE MENÇÕES",
            description=f"**{message.author.display_name}**, você mencionou **{mention_count}** pessoas/cargos!",
            color=0xff8c00
        )
        embed.add_field(
            name="📋 Regra",
            value=f"**Máximo permitido:** 1 menção por mensagem\n**Você mencionou:** {', '.join(mencoes)}",
            inline=False
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await message.channel.send(embed=embed, delete_after=10)
        return  # Para o processamento
    
    # ========================================
    # SISTEMA ANTI-SPAM
    # ========================================
    
    # Adicionar mensagem ao histórico
    message_history[user_id].append(content.lower())
    user_message_times[user_id].append(current_time)
    
    # Verificar spam (mensagens idênticas)
    if len(message_history[user_id]) >= 3:
        recent_messages = list(message_history[user_id])[-3:]
        if len(set(recent_messages)) == 1:  # Todas as mensagens são iguais
            await auto_moderate_spam(message, "spam de mensagens idênticas", f"Enviou 3 mensagens iguais: '{content[:50]}...'")
            return
    
    # ========================================
    # SISTEMA ANTI-FLOOD PROGRESSIVO
    # ========================================
    
    # Determinar limite baseado nos avisos já recebidos
    current_warnings = spam_warnings[user_id]
    
    if current_warnings == 0:
        flood_limit = 5  # Primeira violação: 5 mensagens
    elif current_warnings == 1:
        flood_limit = 4  # Segunda violação: 4 mensagens
    else:
        flood_limit = 3  # Terceira violação: 3 mensagens (ADV)
    
    # Verificar flood (muitas mensagens em pouco tempo)
    if len(user_message_times[user_id]) >= flood_limit:
        recent_times = list(user_message_times[user_id])[-flood_limit:]
        time_diff = recent_times[-1] - recent_times[0]
        
        if time_diff < 8:  # Mensagens em menos de 8 segundos
            await auto_moderate_spam(message, "flood de mensagens", f"Enviou {flood_limit} mensagens em {time_diff:.1f} segundos")
            return
    
    # ========================================
    # SISTEMA ANTI-CAPS
    # ========================================
    
    # Verificar excesso de maiúsculas
    if len(content) > 10:  # Só verificar mensagens com mais de 10 caracteres
        uppercase_count = sum(1 for c in content if c.isupper())
        total_letters = sum(1 for c in content if c.isalpha())
        
        if total_letters > 0:
            caps_percentage = (uppercase_count / total_letters) * 100
            
            if caps_percentage > 70 and total_letters > 15:  # Mais de 70% em caps e mais de 15 letras
                await auto_moderate_spam(message, "excesso de maiúsculas", f"Mensagem com {caps_percentage:.1f}% em maiúsculas")
                return
    
    # Sistema de menção já verificado no início do on_message
    
    # ========================================
    # SISTEMA ANTI-MENSAGEM LONGA (MÁXIMO 90 CARACTERES)
    # ========================================
    
    # Verificar tamanho da mensagem (máximo 90 caracteres)
    if len(content) > 90:
        await auto_moderate_spam(message, "mensagem muito longa", f"Mensagem com {len(content)} caracteres (máximo: 90)")
        return
    
    # ========================================
    # SISTEMA ANTI-EMOJI SPAM
    # ========================================
    
    # Contar emojis (custom e unicode)
    emoji_count = len(message.content.split('😀')) + len(message.content.split('😁')) + len(message.content.split('😂')) + len(message.content.split('🤣')) + len(message.content.split('😃')) + len(message.content.split('😄')) + len(message.content.split('😅')) + len(message.content.split('😆')) + len(message.content.split('😉')) + len(message.content.split('😊')) + len(message.content.split('😋')) + len(message.content.split('😎')) + len(message.content.split('😍')) + len(message.content.split('😘')) + len(message.content.split('🥰')) + len(message.content.split('😗')) + len(message.content.split('😙')) + len(message.content.split('😚')) + len(message.content.split('🙂')) + len(message.content.split('🤗')) + len(message.content.split('🤩')) + len(message.content.split('🤔')) + len(message.content.split('🤨')) + len(message.content.split('😐')) + len(message.content.split('😑')) + len(message.content.split('😶')) + len(message.content.split('🙄')) + len(message.content.split('😏')) + len(message.content.split('😣')) + len(message.content.split('😥')) + len(message.content.split('😮')) + len(message.content.split('🤐')) + len(message.content.split('😯')) + len(message.content.split('😪')) + len(message.content.split('😫')) + len(message.content.split('🥱')) + len(message.content.split('😴')) + len(message.content.split('😌')) + len(message.content.split('😛')) + len(message.content.split('😜')) + len(message.content.split('😝')) + len(message.content.split('🤤')) + len(message.content.split('😒')) + len(message.content.split('😓')) + len(message.content.split('😔')) + len(message.content.split('😕')) + len(message.content.split('🙃')) + len(message.content.split('🤑')) + len(message.content.split('😲')) + len(message.content.split('🙁')) + len(message.content.split('😖')) + len(message.content.split('😞')) + len(message.content.split('😟')) + len(message.content.split('😤')) + len(message.content.split('😢')) + len(message.content.split('😭')) + len(message.content.split('😦')) + len(message.content.split('😧')) + len(message.content.split('😨')) + len(message.content.split('😩')) + len(message.content.split('🤯')) + len(message.content.split('😬')) + len(message.content.split('😰')) + len(message.content.split('😱')) + len(message.content.split('🥵')) + len(message.content.split('🥶')) + len(message.content.split('😳')) + len(message.content.split('🤪')) + len(message.content.split('😵')) + len(message.content.split('🥴')) + len(message.content.split('😠')) + len(message.content.split('😡')) + len(message.content.split('🤬')) + len(message.content.split('😷')) + len(message.content.split('🤒')) + len(message.content.split('🤕')) + len(message.content.split('🤢')) + len(message.content.split('🤮')) + len(message.content.split('🤧')) + len(message.content.split('😇')) + len(message.content.split('🥳')) + len(message.content.split('🥺')) + len(message.content.split('🤠')) + len(message.content.split('🤡')) + len(message.content.split('🤥')) + len(message.content.split('🤫')) + len(message.content.split('🤭')) + len(message.content.split('🧐')) + len(message.content.split('🤓'))
    
    # Método mais simples para contar emojis
    import re
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿☀-⛿✀-➿]')
    unicode_emojis = len(emoji_pattern.findall(content))
    custom_emojis = content.count('<:') + content.count('<a:')
    total_emojis = unicode_emojis + custom_emojis
    
    if total_emojis > 10:
        await auto_moderate_spam(message, "spam de emojis", f"Enviou {total_emojis} emojis em uma mensagem")
        return
    
    # ========================================
    # SISTEMA ANTI-LINK SPAM
    # ========================================
    
    # Verificar links suspeitos (muitos links)
    link_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.br', '.gg']
    link_count = sum(content.lower().count(pattern) for pattern in link_patterns)
    
    if link_count > 3:
        await auto_moderate_spam(message, "spam de links", f"Enviou {link_count} links em uma mensagem")
        return
    
    # ========================================
    # RESPOSTAS AUTOMÁTICAS
    # ========================================
    
    content_lower = content.lower()
    
    # Respostas automáticas
    if 'oi bot' in content_lower or 'olá bot' in content_lower:
        saudacoes = ['Oi! 👋', 'Olá! 😊', 'E aí! 🤗', 'Salve! ✨']
        resposta = random.choice(saudacoes)
        await message.reply(resposta)
    
    elif 'obrigado bot' in content_lower or 'valeu bot' in content_lower:
        agradecimentos = ['De nada! 😊', 'Sempre às ordens! 🤖', 'Fico feliz em ajudar! ✨']
        resposta = random.choice(agradecimentos)
        await message.reply(resposta)
    
    elif 'tchau bot' in content_lower or 'até mais bot' in content_lower:
        despedidas = ['Tchau! 👋', 'Até mais! 😊', 'Falou! 🤗']
        resposta = random.choice(despedidas)
        await message.reply(resposta)
    
    # Processar comandos normalmente
    await bot.process_commands(message)

# ========================================
# SISTEMA DE TICKETS
# ========================================

# Configurações de ticket (salvas em arquivo JSON)
ticket_config = {}

def load_ticket_config():
    """Carrega configurações de ticket"""
    global ticket_config
    try:
        with open('ticket_config.json', 'r') as f:
            ticket_config = json.load(f)
    except:
        ticket_config = {}

def save_ticket_config():
    """Salva configurações de ticket"""
    with open('ticket_config.json', 'w') as f:
        json.dump(ticket_config, f, indent=4)

# Carregar configurações ao iniciar
load_ticket_config()

@bot.command(name='ticket')
@commands.has_permissions(administrator=True)
async def ticket_command(ctx, acao=None, *args):
    """Sistema de tickets - Uso: .ticket [ação]"""
    
    guild_id = str(ctx.guild.id)
    
    if acao is None:
        # Mostrar ajuda
        embed = discord.Embed(
            title="🎫 SISTEMA DE TICKETS",
            description="Configure o sistema de tickets do servidor",
            color=0x00ff88
        )
        embed.add_field(
            name="📋 Comandos Disponíveis",
            value=(
                "`.ticket config` - ⭐ **Configuração interativa** (RECOMENDADO)\n"
                "`.ticket setup` - Cria mensagem de abertura\n"
                "`.ticket categoria [ID]` - Define categoria manualmente\n"
                "`.ticket staff [IDs]` - Define cargos staff manualmente\n"
                "`.ticket mensagem [texto]` - Define mensagem de boas-vindas\n"
                "`.ticket ativar` - Ativa o sistema\n"
                "`.ticket desativar` - Desativa o sistema\n"
                "`.ticket status` - Ver configuração atual"
            ),
            inline=False
        )
        embed.set_footer(text="Sistema de Tickets • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    # Inicializar config do servidor se não existir
    if guild_id not in ticket_config:
        ticket_config[guild_id] = {
            'enabled': False,
            'category_id': None,
            'staff_role_ids': [],
            'welcome_message': 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.'
        }
    
    config = ticket_config[guild_id]
    
    # Ações
    if acao == 'setup':
        # Criar mensagem com botão para abrir ticket
        embed = discord.Embed(
            title="🎫 ABRIR TICKET",
            description="Clique no botão abaixo para abrir um ticket e falar com a equipe!",
            color=0x00ff88
        )
        embed.set_footer(text="Sistema de Tickets • Caos Hub")
        
        view = TicketView()
        await ctx.send(embed=embed, view=view)
        await ctx.reply("✅ Mensagem de ticket criada!")
        
    elif acao == 'categoria':
        if not args:
            await ctx.reply("❌ Uso: `.ticket categoria [ID]`")
            return
        
        category_id = args[0]
        try:
            category = ctx.guild.get_channel(int(category_id))
            if category and isinstance(category, discord.CategoryChannel):
                config['category_id'] = int(category_id)
                save_ticket_config()
                await ctx.reply(f"✅ Categoria definida: **{category.name}**")
            else:
                await ctx.reply("❌ Categoria não encontrada!")
        except:
            await ctx.reply("❌ ID inválido!")
            
    elif acao == 'staff':
        if not args:
            await ctx.reply("❌ Uso: `.ticket staff [IDs separados por vírgula]`")
            return
        
        role_ids = ' '.join(args).replace(' ', '').split(',')
        valid_roles = []
        
        for role_id in role_ids:
            try:
                role = ctx.guild.get_role(int(role_id))
                if role:
                    valid_roles.append(int(role_id))
            except:
                pass
        
        if valid_roles:
            config['staff_role_ids'] = valid_roles
            save_ticket_config()
            await ctx.reply(f"✅ {len(valid_roles)} cargo(s) staff definido(s)!")
        else:
            await ctx.reply("❌ Nenhum cargo válido encontrado!")
            
    elif acao == 'mensagem':
        if not args:
            await ctx.reply("❌ Uso: `.ticket mensagem [texto]`")
            return
        
        message = ' '.join(args)
        config['welcome_message'] = message
        save_ticket_config()
        await ctx.reply("✅ Mensagem de boas-vindas definida!")
        
    elif acao == 'ativar':
        if not config.get('category_id'):
            await ctx.reply("❌ Configure a categoria primeiro! (`.ticket categoria [ID]`)")
            return
        
        config['enabled'] = True
        save_ticket_config()
        await ctx.reply("✅ Sistema de tickets **ATIVADO**!")
        
    elif acao == 'desativar':
        config['enabled'] = False
        save_ticket_config()
        await ctx.reply("✅ Sistema de tickets **DESATIVADO**!")
        
    elif acao == 'status':
        # Mostrar configuração atual
        embed = discord.Embed(
            title="📊 STATUS DO SISTEMA DE TICKETS",
            color=0x00ff88 if config.get('enabled') else 0xff0000
        )
        
        status = "✅ ATIVADO" if config.get('enabled') else "❌ DESATIVADO"
        embed.add_field(name="Status", value=status, inline=False)
        
        if config.get('category_id'):
            category = ctx.guild.get_channel(config['category_id'])
            embed.add_field(name="Categoria", value=category.name if category else "Não encontrada", inline=False)
        else:
            embed.add_field(name="Categoria", value="Não configurada", inline=False)
        
        if config.get('staff_role_ids'):
            roles = [ctx.guild.get_role(rid).mention for rid in config['staff_role_ids'] if ctx.guild.get_role(rid)]
            embed.add_field(name="Cargos Staff", value=', '.join(roles) if roles else "Nenhum", inline=False)
        else:
            embed.add_field(name="Cargos Staff", value="Não configurados", inline=False)
        
        embed.add_field(name="Mensagem", value=config.get('welcome_message', 'Padrão'), inline=False)
        embed.set_footer(text="Sistema de Tickets • Caos Hub")
        
        await ctx.reply(embed=embed)
    
    elif acao == 'config':
        # Painel interativo de configuração
        config_view = TicketConfigView(ctx.guild, guild_id)
        
        embed = discord.Embed(
            title="⚙️ CONFIGURAÇÃO INTERATIVA",
            description="Use os menus abaixo para configurar o sistema de tickets:",
            color=0x00aaff
        )
        embed.add_field(
            name="📋 Passo 1",
            value="Selecione a **Categoria** onde os tickets serão criados",
            inline=False
        )
        embed.add_field(
            name="👮 Passo 2",
            value="Selecione os **Cargos Staff** que poderão ver os tickets",
            inline=False
        )
        embed.add_field(
            name="✅ Passo 3",
            value="Clique em **Salvar Configurações**",
            inline=False
        )
        embed.set_footer(text="Sistema de Tickets • Caos Hub")
        
        await ctx.reply(embed=embed, view=config_view)
    
    # Removido else para não dar erro

@ticket_command.error
async def ticket_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

# View de configuração interativa
class TicketConfigView(discord.ui.View):
    def __init__(self, guild, guild_id):
        super().__init__(timeout=300)
        self.guild = guild
        self.guild_id = guild_id
        self.selected_category = None
        self.selected_roles = []
        
        # Criar dropdown de categorias
        category_options = []
        for category in guild.categories:
            category_options.append(
                discord.SelectOption(
                    label=category.name[:100],
                    description=f"ID: {category.id}",
                    value=str(category.id)
                )
            )
        
        if category_options:
            self.category_select = discord.ui.Select(
                placeholder="📁 Selecione a Categoria",
                options=category_options[:25],  # Discord limita a 25
                row=0
            )
            self.category_select.callback = self.category_callback
            self.add_item(self.category_select)
        
        # Criar dropdown de cargos (apenas cargos de staff específicos)
        role_options = []
        staff_keywords = ['moderador', 'sub moderador', 'staff', 'administrador', 'sub dono', 'founder']
        
        for role in guild.roles:
            if role.name != "@everyone" and not role.managed:  # Exclui @everyone e cargos de bot
                # Verificar se é cargo de staff
                is_staff = any(keyword in role.name.lower() for keyword in staff_keywords)
                
                if is_staff:
                    role_options.append(
                        discord.SelectOption(
                            label=role.name[:100],
                            description=f"ID: {role.id}",
                            value=str(role.id),
                            emoji="👮"
                        )
                    )
        
        if role_options:
            self.role_select = discord.ui.Select(
                placeholder="👮 Selecione os Cargos Staff (múltipla escolha)",
                options=role_options[:25],  # Discord limita a 25
                max_values=min(len(role_options[:25]), 25),
                row=1
            )
            self.role_select.callback = self.role_callback
            self.add_item(self.role_select)
    
    async def category_callback(self, interaction: discord.Interaction):
        self.selected_category = int(self.category_select.values[0])
        category = self.guild.get_channel(self.selected_category)
        await interaction.response.send_message(
            f"✅ Categoria selecionada: **{category.name}**",
            ephemeral=True
        )
    
    async def role_callback(self, interaction: discord.Interaction):
        self.selected_roles = [int(rid) for rid in self.role_select.values]
        roles = [self.guild.get_role(rid).name for rid in self.selected_roles]
        await interaction.response.send_message(
            f"✅ {len(self.selected_roles)} cargo(s) selecionado(s): {', '.join(roles[:5])}{'...' if len(roles) > 5 else ''}",
            ephemeral=True
        )
    
    @discord.ui.button(label="Salvar Configurações", style=discord.ButtonStyle.green, emoji="💾", row=2)
    async def save_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_category:
            await interaction.response.send_message("❌ Selecione uma categoria primeiro!", ephemeral=True)
            return
        
        if not self.selected_roles:
            await interaction.response.send_message("❌ Selecione pelo menos um cargo staff!", ephemeral=True)
            return
        
        # Salvar configurações
        if self.guild_id not in ticket_config:
            ticket_config[self.guild_id] = {}
        
        ticket_config[self.guild_id]['category_id'] = self.selected_category
        ticket_config[self.guild_id]['staff_role_ids'] = self.selected_roles
        ticket_config[self.guild_id]['enabled'] = True
        
        if 'welcome_message' not in ticket_config[self.guild_id]:
            ticket_config[self.guild_id]['welcome_message'] = 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.'
        
        save_ticket_config()
        
        category = self.guild.get_channel(self.selected_category)
        roles = [self.guild.get_role(rid).mention for rid in self.selected_roles]
        
        embed = discord.Embed(
            title="✅ CONFIGURAÇÕES SALVAS!",
            description="Sistema de tickets configurado com sucesso!",
            color=0x00ff00
        )
        embed.add_field(
            name="📁 Categoria",
            value=category.mention,
            inline=False
        )
        embed.add_field(
            name="👮 Cargos Staff",
            value=", ".join(roles),
            inline=False
        )
        embed.add_field(
            name="🎫 Próximo Passo",
            value="Use `.ticket setup` para criar a mensagem de abertura!",
            inline=False
        )
        embed.set_footer(text="Sistema de Tickets • Caos Hub")
        
        await interaction.response.send_message(embed=embed)
        self.stop()

# Painel de seleção de categoria
class TicketCategoryView(discord.ui.View):
    def __init__(self, config, category_channel, user):
        super().__init__(timeout=300)  # 5 minutos
        self.config = config
        self.category_channel = category_channel
        self.user = user
        self.selected_category = "📁 Geral"
        self.selected_priority = "🟡 Média"
    
    @discord.ui.select(
        placeholder="🏷️ Selecione a Categoria do Ticket",
        options=[
            discord.SelectOption(label="Geral", description="Assuntos gerais", emoji="📁", value="geral"),
            discord.SelectOption(label="Compras", description="Dúvidas sobre compras", emoji="🛒", value="compras"),
            discord.SelectOption(label="Suporte Técnico", description="Problemas técnicos", emoji="🔧", value="tecnico"),
            discord.SelectOption(label="Denúncia", description="Reportar usuário/conteúdo", emoji="🚨", value="denuncia"),
            discord.SelectOption(label="Parceria", description="Proposta de parceria", emoji="🤝", value="parceria"),
            discord.SelectOption(label="Financeiro", description="Questões de pagamento", emoji="💰", value="financeiro"),
            discord.SelectOption(label="Moderação", description="Questões de moderação", emoji="🛡️", value="moderacao"),
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        
        category_map = {
            "geral": "📁 Geral",
            "compras": "🛒 Compras",
            "tecnico": "🔧 Suporte Técnico",
            "denuncia": "🚨 Denúncia",
            "parceria": "🤝 Parceria",
            "financeiro": "💰 Financeiro",
            "moderacao": "🛡️ Moderação"
        }
        
        self.selected_category = category_map.get(select.values[0], "📁 Geral")
        await interaction.response.send_message(f"✅ Categoria selecionada: **{self.selected_category}**", ephemeral=True)
    
    @discord.ui.select(
        placeholder="⚡ Selecione a Prioridade",
        options=[
            discord.SelectOption(label="Baixa", description="Não é urgente", emoji="🟢", value="baixa"),
            discord.SelectOption(label="Média", description="Prioridade normal", emoji="🟡", value="media"),
            discord.SelectOption(label="Alta", description="Precisa de atenção", emoji="🟠", value="alta"),
            discord.SelectOption(label="Urgente", description="Muito urgente!", emoji="🔴", value="urgente"),
        ]
    )
    async def select_priority(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        
        priority_map = {
            "baixa": "🟢 Baixa",
            "media": "🟡 Média",
            "alta": "🟠 Alta",
            "urgente": "🔴 Urgente"
        }
        
        self.selected_priority = priority_map.get(select.values[0], "🟡 Média")
        await interaction.response.send_message(f"✅ Prioridade selecionada: **{self.selected_priority}**", ephemeral=True)
    
    @discord.ui.button(label="Continuar", style=discord.ButtonStyle.green, emoji="✅", row=2)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        
        # Abrir modal com as seleções salvas
        modal = TicketModal(self.config, self.category_channel, self.selected_category, self.selected_priority)
        await interaction.response.send_modal(modal)
        self.stop()

# Modal para coletar informações do ticket (com seleções salvas)
class TicketModal(discord.ui.Modal, title="🎫 Informações do Ticket"):
    def __init__(self, config, category, selected_category, selected_priority):
        super().__init__()
        self.config = config
        self.category = category
        self.selected_category = selected_category
        self.selected_priority = selected_priority
        
        # Campo 1: Assunto (OBRIGATÓRIO)
        self.assunto = discord.ui.TextInput(
            label="📋 Assunto do Ticket",
            placeholder="Ex: Dúvida sobre cargos, Bug no bot, etc.",
            required=True,
            max_length=100,
            min_length=3
        )
        self.add_item(self.assunto)
        
        # Campo 2: Descrição (OBRIGATÓRIO)
        self.descricao = discord.ui.TextInput(
            label="📝 Descrição Detalhada",
            placeholder="Descreva seu problema, dúvida ou solicitação com detalhes...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
            min_length=10
        )
        self.add_item(self.descricao)
        
        # Campo 3: Idioma (OBRIGATÓRIO)
        self.idioma = discord.ui.TextInput(
            label="🌐 Seu Idioma",
            placeholder="Ex: Português, English, Español, etc.",
            required=True,
            max_length=50
        )
        self.add_item(self.idioma)
        
        # Campo 4: Informações Adicionais (OPCIONAL)
        self.info_adicional = discord.ui.TextInput(
            label="ℹ️ Informações Adicionais (Opcional)",
            placeholder="Links, prints, IDs de usuários, etc.",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.add_item(self.info_adicional)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Usar seleções salvas do painel
            categoria_valor = self.selected_category
            prioridade_valor = self.selected_priority
            info_adicional_valor = self.info_adicional.value.strip() if self.info_adicional.value else "Nenhuma informação adicional fornecida"
            
            # Definir cor baseado na prioridade selecionada
            if "🔴" in prioridade_valor or "🟠" in prioridade_valor:
                cor_embed = 0xff0000  # Vermelho
            elif "🟢" in prioridade_valor:
                cor_embed = 0x00ff00  # Verde
            else:
                cor_embed = 0xffaa00  # Laranja (Média)
                emoji_prioridade = prioridade_valor.split()[0]  # Pega o emoji
            
            # Buscar categoria configurada
            category_id = self.config.get('category_id')
            
            if not category_id:
                await interaction.response.send_message("❌ Sistema não configurado! Use `.ticket categoria [ID]`", ephemeral=True)
                return
            
            # Buscar em todas as categorias do servidor
            target_category = None
            for cat in interaction.guild.categories:
                if cat.id == int(category_id):
                    target_category = cat
                    break
            
            if not target_category:
                await interaction.response.send_message("❌ Categoria não encontrada! Reconfigure com `.ticket categoria [ID]`", ephemeral=True)
                return
            
            # Criar canal de ticket
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Adicionar permissões para staff
            for role_id in self.config.get('staff_role_ids', []):
                role = interaction.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Contar quantos tickets já existem na categoria para numeração
            ticket_number = 1
            for channel in target_category.channels:
                if channel.name.startswith("carrinho-"):
                    try:
                        num = int(channel.name.split("-")[1])
                        if num >= ticket_number:
                            ticket_number = num + 1
                    except:
                        pass
            
            # Criar canal com nome numerado
            ticket_channel = await target_category.create_text_channel(
                name=f"⌊🛒⌉-carrinho-{ticket_number}",
                overwrites=overwrites
            )
            
            # Embed BONITO com todas as informações
            embed = discord.Embed(
                title="🎫 NOVO TICKET ABERTO",
                description=f"**{self.config.get('welcome_message')}**\n\n*Nossa equipe responderá o mais breve possível!*",
                color=cor_embed,
                timestamp=discord.utils.utcnow()
            )
            
            # Informações do usuário
            embed.set_author(
                name=f"Ticket de {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Campos organizados
            embed.add_field(
                name="👤 Aberto por",
                value=f"{interaction.user.mention}\n`ID: {interaction.user.id}`",
                inline=True
            )
            
            embed.add_field(
                name="🏷️ Categoria",
                value=categoria_valor,
                inline=True
            )
            
            embed.add_field(
                name="⚡ Prioridade",
                value=prioridade_valor,
                inline=True
            )
            
            embed.add_field(
                name="🌐 Idioma",
                value=f"**{self.idioma.value}**",
                inline=True
            )
            
            embed.add_field(
                name="📋 Assunto",
                value=f"```{self.assunto.value}```",
                inline=False
            )
            
            embed.add_field(
                name="📝 Descrição Detalhada",
                value=self.descricao.value[:1000],
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Informações Adicionais",
                value=info_adicional_valor[:500],
                inline=False
            )
            
            embed.set_footer(
                text="Sistema de Tickets • Caos Hub",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            # View com botão para fechar
            close_view = CloseTicketView()
            await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=close_view)
            
            # Mensagem de confirmação
            await interaction.response.send_message(
                f"✅ **Ticket criado com sucesso!**\n\n"
                f"📌 Canal: {ticket_channel.mention}\n"
                f"🏷️ Categoria: **{categoria_valor}**\n"
                f"⚡ Prioridade: **{prioridade_valor}**\n\n"
                f"*Nossa equipe foi notificada e responderá em breve!*",
                ephemeral=True
            )
        
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ **Erro de Permissão!**\n\n"
                "O bot não tem permissão para criar canais nesta categoria.\n"
                "Verifique as permissões do bot!",
                ephemeral=True
            )
        except Exception as e:
            print(f"[ERRO TICKET] {e}")
            await interaction.response.send_message(
                f"❌ **Erro ao criar ticket!**\n\n"
                f"Detalhes: `{str(e)}`\n\n"
                f"Entre em contato com um administrador!",
                ephemeral=True
            )

# View com botão para abrir ticket
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = str(interaction.guild.id)
        
        # Verificar se o sistema está ativado
        if guild_id not in ticket_config or not ticket_config[guild_id].get('enabled'):
            await interaction.response.send_message("❌ Sistema de tickets desativado!", ephemeral=True)
            return
        
        config = ticket_config[guild_id]
        category_id = config.get('category_id')
        
        if not category_id:
            await interaction.response.send_message("❌ Sistema não configurado!", ephemeral=True)
            return
        
        category = interaction.guild.get_channel(category_id)
        if not category:
            await interaction.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
            return
        
        # Verificar se o usuário já tem um ticket aberto
        for channel in category.channels:
            if channel.name.endswith(f"-{interaction.user.id}"):
                await interaction.response.send_message(f"❌ Você já tem um ticket aberto: {channel.mention}", ephemeral=True)
                return
        
        # Mostrar painel de seleção
        panel_embed = discord.Embed(
            title="🎫 CONFIGURAR SEU TICKET",
            description="**Selecione as opções abaixo antes de continuar:**\n\n"
                       "🏷️ **Categoria** - Tipo do seu ticket\n"
                       "⚡ **Prioridade** - Urgência do atendimento\n\n"
                       "*Após selecionar, clique em ✅ Continuar*",
            color=0x00ff88
        )
        panel_embed.set_footer(text="As seleções são salvas automaticamente")
        
        panel_view = TicketCategoryView(config, category, interaction.user)
        await interaction.response.send_message(embed=panel_embed, view=panel_view, ephemeral=True)

# View com botão para fechar ticket
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Apenas staff pode fechar!", ephemeral=True)
            return
        
        # CANAL DE LOG
        log_channel_id = 1424050835460980889
        log_channel = interaction.guild.get_channel(log_channel_id)
        
        if log_channel:
            try:
                ticket_channel = interaction.channel
                
                # Coletar mensagens do ticket
                messages = []
                async for msg in ticket_channel.history(limit=100, oldest_first=True):
                    messages.append(msg)
                
                # EMBED DE LOG DETALHADO
                log_embed = discord.Embed(
                    title="🔒 TICKET FECHADO",
                    description=f"**Canal:** {ticket_channel.name}\n**ID:** `{ticket_channel.id}`",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                )
                
                # Extrair informações do primeiro embed
                if messages and messages[0].embeds:
                    embed_inicial = messages[0].embeds[0]
                    
                    for field in embed_inicial.fields:
                        if "Aberto por" in field.name:
                            log_embed.add_field(name="👤 Aberto por", value=field.value, inline=True)
                        elif "Assunto" in field.name:
                            log_embed.add_field(name="📋 Assunto", value=field.value, inline=False)
                        elif "Descrição" in field.name:
                            log_embed.add_field(name="📝 Descrição", value=field.value[:1024], inline=False)
                        elif "Info Adicional" in field.name:
                            log_embed.add_field(name="ℹ️ Info Adicional", value=field.value[:1024], inline=False)
                
                # Quem fechou
                log_embed.add_field(
                    name="🔒 Fechado por",
                    value=f"{interaction.user.mention}\n`ID: {interaction.user.id}`",
                    inline=True
                )
                
                # Estatísticas
                total_mensagens = len(messages)
                usuarios_participantes = len(set(msg.author.id for msg in messages if not msg.author.bot))
                
                log_embed.add_field(
                    name="📊 Estatísticas",
                    value=f"**Mensagens:** {total_mensagens}\n**Participantes:** {usuarios_participantes}",
                    inline=True
                )
                
                # Duração
                if messages:
                    criado_em = messages[0].created_at
                    fechado_em = discord.utils.utcnow()
                    duracao = fechado_em - criado_em
                    
                    horas = int(duracao.total_seconds() // 3600)
                    minutos = int((duracao.total_seconds() % 3600) // 60)
                    
                    log_embed.add_field(
                        name="⏱️ Duração",
                        value=f"{horas}h {minutos}m",
                        inline=True
                    )
                
                log_embed.set_footer(text="Sistema de Tickets • Caos Hub")
                
                # Enviar embed
                await log_channel.send(embed=log_embed)
                
                # CRIAR ARQUIVO COM HISTÓRICO COMPLETO
                historico_texto = f"=== HISTÓRICO DO TICKET: {ticket_channel.name} ===\n\n"
                
                for msg in messages:
                    timestamp = msg.created_at.strftime("%d/%m/%Y %H:%M:%S")
                    autor = f"{msg.author.display_name} ({msg.author.id})"
                    conteudo = msg.content if msg.content else "[Embed ou anexo]"
                    
                    historico_texto += f"[{timestamp}] {autor}:\n{conteudo}\n\n"
                
                # Enviar arquivo
                import io
                arquivo = discord.File(
                    io.BytesIO(historico_texto.encode('utf-8')),
                    filename=f"ticket_{ticket_channel.name}_{discord.utils.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                
                await log_channel.send(
                    content=f"📄 **Histórico completo do ticket `{ticket_channel.name}`:**",
                    file=arquivo
                )
                
            except Exception as e:
                print(f"[ERRO LOG TICKET] {e}")
        
        await interaction.response.send_message("🔒 Fechando ticket...", ephemeral=True)
        await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user}")

# ========================================
# SISTEMA AUTOMÁTICO DE NICKNAMES
# ========================================

# FUNÇÃO DESABILITADA - CAUSAVA DUPLICAÇÕES
async def update_nickname_for_roles_DISABLED(member):
    """Atualiza o nickname do membro baseado nos cargos que possui"""
    try:
        # Salvar nickname original se ainda não foi salvo (SEM prefixos)
        if member.id not in original_nicknames:
            clean_name = member.display_name
            # Remover qualquer prefixo existente para salvar o nome limpo
            for prefix in CARGO_PREFIXES.values():
                if clean_name.startswith(prefix + " "):
                    clean_name = clean_name[len(prefix + " "):]
                    break
            original_nicknames[member.id] = clean_name
        
        # Verificar se o membro tem algum cargo com prefixo
        prefixes_to_add = []
        for role in member.roles:
            if role.id in CARGO_PREFIXES:
                prefix = CARGO_PREFIXES[role.id]
                if prefix not in prefixes_to_add:
                    prefixes_to_add.append(prefix)
        
        # Obter nickname original (sem prefixos)
        original_nick = original_nicknames.get(member.id, member.name)
        
        # Remover prefixos existentes do nickname atual
        current_nick = member.display_name
        for prefix in CARGO_PREFIXES.values():
            if current_nick.startswith(prefix + " "):
                current_nick = current_nick[len(prefix + " "):]
        
        # Construir novo nickname
        if prefixes_to_add:
            # Ordenar prefixos por importância (admin > mod > vip, etc)
            priority_order = ["[OWNER]", "[ADMIN]", "[MOD]", "[SUB]", "[STAFF]", "[DEV]", "[DESIGN]", "[YT]", "[LIVE]", "[VIP]", "[PREMIUM]", "[BOOST]"]
            prefixes_to_add.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)
            
            # Usar apenas o prefixo de maior prioridade
            new_nickname = f"{prefixes_to_add[0]} {current_nick}"
        else:
            # Sem cargos especiais, usar nickname original
            new_nickname = original_nick
        
        # Limitar tamanho do nickname (Discord tem limite de 32 caracteres)
        if len(new_nickname) > 32:
            # Truncar o nome mas manter o prefixo
            if prefixes_to_add:
                prefix = prefixes_to_add[0]
                max_name_length = 32 - len(prefix) - 1  # -1 para o espaço
                truncated_name = current_nick[:max_name_length]
                new_nickname = f"{prefix} {truncated_name}"
            else:
                new_nickname = new_nickname[:32]
        
        # Atualizar nickname se mudou
        if member.display_name != new_nickname:
            await member.edit(nick=new_nickname, reason="Atualização automática de nickname por cargo")
            print(f"✅ Nickname atualizado: {member.name} -> {new_nickname}")
            return True
        
        return False
        
    except discord.Forbidden:
        print(f"❌ Sem permissão para alterar nickname de {member.display_name}")
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar nickname de {member.display_name}: {e}")
        return False

# Evento COMPLETAMENTE removido para evitar duplicações

# Comando para atualizar nicknames manualmente
# COMANDO DESABILITADO - CAUSAVA DUPLICAÇÕES
# @bot.command(name='updatenicks')
# @commands.has_permissions(administrator=True)
async def update_nicks_command_DISABLED(ctx):
    """Atualiza os nicknames de todos os membros baseado nos cargos"""
    
    embed_start = discord.Embed(
        title="🔄 ATUALIZANDO NICKNAMES",
        description="Iniciando atualização automática de nicknames...",
        color=0x00ff00
    )
    msg = await ctx.reply(embed=embed_start)
    
    updated_count = 0
    total_members = len([m for m in ctx.guild.members if not m.bot])
    
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        # success = await update_nickname_for_roles_DISABLED(member)
        success = False  # Desabilitado
        if success:
            updated_count += 1
        
        # Pequena pausa para evitar rate limit
        await asyncio.sleep(0.1)
    
    embed_result = discord.Embed(
        title="✅ NICKNAMES ATUALIZADOS",
        description=f"**Processo concluído!**\n\n📊 **Estatísticas:**\n👥 **Membros processados:** {total_members}\n✅ **Nicknames atualizados:** {updated_count}\n🎯 **Taxa de sucesso:** {(updated_count/total_members*100):.1f}%",
        color=0x00ff00
    )
    embed_result.add_field(
        name="🔧 Cargos Monitorados",
        value="• `Administrador` → `[ADM]`\n• `Staff` → `[STF]`\n• `Moderador` → `[MOD]`\n• `Sub Moderador` → `[SBM]`",
        inline=False
    )
    embed_result.set_footer(text="Sistema de Nicknames Automáticos • Caos Hub")
    
    await msg.edit(embed=embed_result)

# @update_nicks_command.error
# async def update_nicks_error(ctx, error):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

# ========================================
# COMANDO ADDROLE - ADICIONAR CARGOS E PREFIXOS
# ========================================

@bot.command(name='addrole')
@is_sub_moderator_or_higher()
async def add_role_new(ctx, cargo: discord.Role = None, usuario: discord.Member = None):
    """Adiciona cargo com hierarquia automática e prefixo"""

    if not cargo or not usuario:
        embed = discord.Embed(
            title="❌ Uso Incorreto",
            description="Use: `.addrole @cargo @usuário` ",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return

    # Recarregar membro para garantir que roles estão atualizadas
    usuario = await ctx.guild.fetch_member(usuario.id)

    if cargo in usuario.roles:
        embed = discord.Embed(
            title="⚠️ Cargo Já Possui",
            description=f"**{usuario.display_name}** já possui o cargo **{cargo.name}**!",
            color=0xffaa00
        )
        embed.add_field(name="📋 Informação", value=f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo.mention}", inline=False)
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    try:
        HIERARCHY = {
            1365633918593794079: 4,  # ADM
            1365634226254254150: 3,  # STF
            1365633102973763595: 2,  # MOD
            1365631940434333748: 1   # SBM
        }

        removed_roles = []

        # Remover cargos conflitantes de mesma hierarquia
        if cargo.id in HIERARCHY:
            for role in list(usuario.roles):
                if role.id in HIERARCHY and role.id != cargo.id:
                    await usuario.remove_roles(role)
                    removed_roles.append(role.name)

        await usuario.add_roles(cargo)
        
        # Atualizar nickname se houver prefixo
        nickname_msg = ""
        if cargo.id in CARGO_PREFIXES:
            clean_name = usuario.display_name
            for prefix in CARGO_PREFIXES.values():
                if clean_name.startswith(prefix + " "):
                    clean_name = clean_name[len(prefix) + 1:]
                    break

            new_nickname = f"{CARGO_PREFIXES[cargo.id]} {clean_name}"
            if len(new_nickname) > 32:
                clean_name = clean_name[:32 - len(CARGO_PREFIXES[cargo.id]) - 1]
                new_nickname = f"{CARGO_PREFIXES[cargo.id]} {clean_name}"

            await usuario.edit(nick=new_nickname)
            nickname_msg = f"\n🏷️ **Nickname:** `{new_nickname}` "
        
        embed = discord.Embed(
            title="✅ CARGO ADICIONADO",
            description=f"**{cargo.name}** foi adicionado a **{usuario.display_name}**!",
            color=0x00ff00
        )

        details = f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo.mention}\n**Moderador:** {ctx.author.mention}"
        if removed_roles:
            details += f"\n🔄 **Removidos:** {', '.join(removed_roles)}"
        details += nickname_msg

        embed.add_field(name="📋 Detalhes", value=details, inline=False)
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(title="❌ ERRO", description=f"Erro ao adicionar cargo: {e}", color=0xff0000)
        await ctx.reply(embed=embed)

@add_role_new.error
async def addrole_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="❌ Permissão Negada",
            description="Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.RoleNotFound):
        embed = discord.Embed(
            title="❌ Cargo Não Encontrado",
            description="Cargo não encontrado! Certifique-se de mencionar um cargo válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Usuário não encontrado! Certifique-se de mencionar um usuário válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.RoleNotFound):
        embed = discord.Embed(
            title="❌ Cargo Não Encontrado",
            description="Cargo não encontrado! Certifique-se de mencionar um cargo válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Usuário não encontrado! Certifique-se de mencionar um usuário válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)

# ========================================
# COMANDO REMOVEROLE - REMOVER CARGOS
# ========================================

@bot.command(name='removerole')
@is_sub_moderator_or_higher()
async def remove_role_new(ctx, cargo: discord.Role = None, usuario: discord.Member = None):
    """Remove cargo e restaura nickname com hierarquia"""

    if not cargo or not usuario:
        embed = discord.Embed(
            title="❌ Uso Incorreto",
            description="Use: `.removerole @cargo @usuário` ",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return

    usuario = await ctx.guild.fetch_member(usuario.id)

    if cargo not in usuario.roles:
        embed = discord.Embed(
            title="⚠️ Cargo Não Possui",
            description=f"**{usuario.display_name}** não possui **{cargo.name}**!",
            color=0xffaa00
        )
        await ctx.reply(embed=embed)
        return
    
    try:
        HIERARCHY = {
            1365633918593794079: 4,  # ADM
            1365634226254254150: 3,  # STF
            1365633102973763595: 2,  # MOD
            1365631940434333748: 1   # SBM
        }

        await usuario.remove_roles(cargo)
        usuario = await ctx.guild.fetch_member(usuario.id)  # Garantir roles atualizadas
        
        nickname_msg = ""
        if cargo.id in CARGO_PREFIXES:
            clean_name = usuario.display_name
            for prefix in CARGO_PREFIXES.values():
                if clean_name.startswith(prefix + " "):
                    clean_name = clean_name[len(prefix) + 1:]
                    break

            # Encontrar o prefixo de maior cargo restante
            highest_role = None
            highest_level = 0
            for role in usuario.roles:
                if role.id in HIERARCHY and role.id in CARGO_PREFIXES:
                    if HIERARCHY[role.id] > highest_level:
                        highest_level = HIERARCHY[role.id]
                        highest_role = role

            if highest_role:
                new_nickname = f"{CARGO_PREFIXES[highest_role.id]} {clean_name}"
                await usuario.edit(nick=new_nickname)
                nickname_msg = f"\n🏷️ **Nickname atualizado:** `{new_nickname}` "
            else:
                await usuario.edit(nick=clean_name)
                nickname_msg = f"\n🏷️ **Nickname restaurado:** `{clean_name}` "
        
        embed = discord.Embed(
            title="✅ CARGO REMOVIDO",
            description=f"**{cargo.name}** foi removido de **{usuario.display_name}**!",
            color=0xff4444
        )

        details = f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo.mention}\n**Moderador:** {ctx.author.mention}{nickname_msg}"
        embed.add_field(name="📋 Detalhes", value=details, inline=False)
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(title="❌ ERRO", description=f"Erro ao remover cargo: {e}", color=0xff0000)
        await ctx.reply(embed=embed)

@remove_role_new.error
async def removerole_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="❌ Permissão Negada",
            description="Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.RoleNotFound):
        embed = discord.Embed(
            title="❌ Cargo Não Encontrado",
            description="Cargo não encontrado! Certifique-se de mencionar um cargo válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Usuário não encontrado! Certifique-se de mencionar um usuário válido.",
            color=0xff0000
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)

# ========================================
# CONFIGURAÇÃO E INICIALIZAÇÃO
# ========================================

# ========================================
# SERVIDOR HTTP PARA UPTIMEROBOT (ANTI-HIBERNAÇÃO)
# ========================================
# Este servidor recebe pings do UptimeRobot para manter o bot acordado 24/7

class HealthHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Responde às requisições HEAD do UptimeRobot"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Log do ping HEAD recebido
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f'🌐 [{current_time}] HEAD request do UptimeRobot - Bot mantido acordado!')
    
    def do_GET(self):
        """Responde aos pings do UptimeRobot"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Página HTML bonita para mostrar status
        uptime = time.time() - start_time if 'start_time' in globals() else 0
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Caos Bot - Status</title>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    background: rgba(0,0,0,0.3);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }}
                h1 {{ font-size: 3em; margin: 0; }}
                .status {{ color: #00ff88; font-size: 1.5em; margin: 20px 0; }}
                .info {{ font-size: 1.2em; opacity: 0.9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Caos Bot</h1>
                <div class="status">✅ ONLINE 24/7</div>
                <div class="info">⏱️ Uptime: {hours}h {minutes}m</div>
                <div class="info">🔄 Sistema Anti-Hibernação Ativo</div>
                <div class="info">💚 Mantido pelo UptimeRobot</div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
        
        # Log do ping recebido
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f'🌐 [{current_time}] GET request do UptimeRobot - Bot mantido acordado!')
    
    def log_message(self, format, *args):
        pass  # Silencia logs HTTP padrão

def start_http_server():
    """Inicia servidor HTTP para receber pings do UptimeRobot"""
    global start_time
    start_time = time.time()
    
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'🌐 Servidor HTTP iniciado na porta {port}')
    print(f'🔗 URL do bot: https://seu-app.onrender.com')
    print(f'📍 Configure no UptimeRobot: Ping a cada 5 minutos')
    server.serve_forever()

# Token do bot principal (usando variável de ambiente para segurança)
TOKEN = os.getenv('DISCORD_TOKEN')

# ========================================
# SISTEMA DE MÚSICA COM WAVELINK/LAVALINK
# ========================================
"""
Sistema profissional de música usando Wavelink (Lavalink).
Muito mais estável que yt-dlp direto.
Lavalink roda localmente no mesmo container (localhost:2333).
"""

# Configuração do Lavalink (local no mesmo container)
# NOTA: Já definido no início do arquivo, não redefinir aqui

# Cores padrão para embeds
COLOR_SUCCESS = 0xff8c00  # Laranja
COLOR_ERROR = 0xff4d4d    # Vermelho

# Sistema de música removido - foco em moderação e vendas

# Pool global de bots (para rastreamento)
music_bots_pool = {}

# Pool de controle de disponibilidade
bot_pool = {
    'CAOS Music 1': {'busy': False, 'guild_id': None},
    'CAOS Music 2': {'busy': False, 'guild_id': None},
    'CAOS Music 3': {'busy': False, 'guild_id': None},
    'CAOS Music 4': {'busy': False, 'guild_id': None},
}

def pick_available_bot(guild_id):
    """Retorna o bot designado para este guild ou um livre"""
    # Verificar se já tem bot designado para este guild
    for name, info in bot_pool.items():
        if info['guild_id'] == guild_id and info['busy']:
            return name
    
    # Nenhum designado, pegar primeiro livre
    for name, info in bot_pool.items():
        if not info['busy']:
            return name
    
    return None  # Todos ocupados

def mark_bot_busy(name, guild_id):
    """Marca bot como ocupado"""
    if name in bot_pool:
        bot_pool[name]['busy'] = True
        bot_pool[name]['guild_id'] = guild_id
        print(f'[POOL] 🔒 {name} ocupado no servidor {guild_id}')

def mark_bot_free(name):
    """Libera bot"""
    if name in bot_pool:
        guild_id = bot_pool[name]['guild_id']
        bot_pool[name]['busy'] = False
        bot_pool[name]['guild_id'] = None
        print(f'[Pool] 🔓 {name} liberado (estava em {guild_id})')

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def placeholder_function():
    pass

# ========================================
# INICIALIZAÇÃO DO BOT
# ========================================

# Função temporária removida - código de música deletado

# ===== TEMP =====
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.voice_states = True
    
    music_bot = commands.Bot(command_prefix='mc.', intents=intents, help_command=None)
    
    # Fila ISOLADA para este bot
    bot_queues = {}
    
    def get_bot_queue(guild_id):
        if guild_id not in bot_queues:
            bot_queues[guild_id] = MusicQueue()
        return bot_queues[guild_id]
    
    # Função para retornar o nome (evita closure)
    def this_name():
        return bot_name
    
    @music_bot.event
    async def on_ready(bot_name=bot_name, music_bot=music_bot):
        print(f'✅ {music_bot.user} ({bot_name}) is online. Trying to connect to Lavalink...')
        print(f'📊 [{music_bot.user}] conectado em {len(music_bot.guilds)} servidor(es)')
        
        # Status personalizado
        try:
            await music_bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name="mc.p | mc.play"),
                status=discord.Status.online
            )
        except Exception as e:
            print(f"[{bot_name}] Erro ao definir status: {e}")
        
        # Conectar ao Lavalink com retry robusto
        try:
            await connect_lavalink(music_bot, identifier=bot_name)
            music_bots_pool[bot_name] = {'bot': music_bot, 'online': True}
            print(f"[{bot_name}] Lavalink connected.")
        except Exception as e:
            print(f"[{bot_name}] Lavalink connect failed: {e}")
    
    @music_bot.event
    async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
        """Auto-play próxima música"""
        player = payload.player
        if not player:
            return
        
        queue_obj = get_bot_queue(player.guild.id)
        
        # Loop de música
        if queue_obj.loop_mode == 'song' and queue_obj.current:
            await player.play(queue_obj.current)
            await player.set_volume(queue_obj.volume)
            print(f'[{bot_name}] 🔂 Loop: {queue_obj.current.title}')
            return
        
        # Próxima da fila
        if queue_obj.queue:
            next_track = queue_obj.queue.popleft()
            queue_obj.current = next_track
            queue_obj.skip_votes.clear()
            
            await player.play(next_track)
            await player.set_volume(queue_obj.volume)
            print(f'[{bot_name}] ⏭️ Próxima: {next_track.title}')
        else:
            # Fila vazia, liberar bot
            mark_bot_free(bot_name)
            queue_obj.bot_name = None
    
    # Helper para verificar se este bot é o designado
    def is_assigned_for_guild(guild_id):
        """Verifica se este bot é o designado para o guild"""
        assigned = pick_available_bot(guild_id)
        # Se não houver atribuição e este bot estiver livre, pode assumir
        if assigned is None and not bot_pool[bot_name]['busy']:
            return True
        return assigned == bot_name
    
    @music_bot.command(name='play', aliases=['p'])
    async def play_cmd(ctx, *, query: str):
        """mc.play <música> ou mc.p <música>"""
        bot_name = this_name()
        guild_id = ctx.guild.id

        # 1) Só responde se designado
        if not is_assigned_for_guild(guild_id):
            return

        # 2) Se o usuário não estiver em um canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply(embed=discord.Embed(
                description="❌ Você precisa estar em um canal de voz!",
                color=COLOR_ERROR
            ))

        # 3) Verifica se há nodes conectados (auto-reconexão)
        if not any(node.status == wavelink.NodeStatus.CONNECTED for node in wavelink.Pool.nodes.values()):
            msg = await ctx.reply(embed=discord.Embed(
                description="🔌 Nenhum node Lavalink conectado. Tentando reconectar...",
                color=COLOR_SUCCESS
            ))
            success = await connect_lavalink(ctx.bot, identifier=bot_name)
            if not success:
                return await msg.edit(embed=discord.Embed(
                    description="❌ Falha ao reconectar com o Lavalink.",
                    color=COLOR_ERROR
                ))
            await asyncio.sleep(3)
            await msg.delete()

        # 4) Marcar bot ocupado
        mark_bot_busy(bot_name, guild_id)
        queue_obj = get_bot_queue(guild_id)
        queue_obj.bot_name = bot_name

        # 5) Buscar música
        try:
            track = await wavelink.YouTubeTrack.search(query, return_first=True)
            if not track:
                mark_bot_free(bot_name)
                return await ctx.reply(embed=discord.Embed(
                    description="❌ Nenhum resultado encontrado.",
                    color=COLOR_ERROR
                ))
        except Exception as e:
            mark_bot_free(bot_name)
            return await ctx.reply(embed=discord.Embed(
                description=f"❌ Erro ao buscar: {str(e)[:150]}",
                color=COLOR_ERROR
            ))

        # 6) Conectar ao canal de voz
        try:
            vc: wavelink.Player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)
            print(f'[{bot_name}] 🔊 Conectado ao canal de voz em {ctx.guild.name}')
        except Exception as e:
            mark_bot_free(bot_name)
            return await ctx.reply(embed=discord.Embed(
                description=f"❌ Erro ao conectar no canal de voz: {e}",
                color=COLOR_ERROR
            ))

        # 7) Se já está tocando, adicionar à fila
        if vc.playing:
            queue_obj.queue.append(track)
            embed = discord.Embed(
                title="📋 Adicionado à fila",
                description=f"**{track.title}**",
                color=COLOR_SUCCESS
            )
            embed.add_field(name="Posição", value=f"#{len(queue_obj.queue)}", inline=True)
            embed.set_footer(text=f"Bot: {bot_name}")
            return await ctx.reply(embed=embed)

        # 8) Tocar música
        queue_obj.current = track
        queue_obj.current_requester = ctx.author.id
        queue_obj.skip_votes.clear()

        try:
            await vc.play(track)
            await vc.set_volume(queue_obj.volume)
        except Exception as e:
            mark_bot_free(bot_name)
            return await ctx.reply(embed=discord.Embed(
                description=f"❌ Erro ao tocar: {e}",
                color=COLOR_ERROR
            ))

        print(f'[{bot_name}] ▶️ Tocando: {track.title} em {ctx.guild.name}')

        # 9) Criar painel
        try:
            view = MusicControlPanel(ctx, queue_obj)
            embed_panel = await view.create_embed()
            panel_msg = await ctx.send(embed=embed_panel, view=view)
            queue_obj.control_message = panel_msg
            queue_obj.control_view = view
        except:
            pass

        # 10) Mensagem de sucesso
        embed = discord.Embed(
            description=f"▶️ Tocando agora: **{track.title}**",
            color=COLOR_SUCCESS
        )
        await ctx.reply(embed=embed)
    
    @music_bot.command(name='skip', aliases=['s'])
    async def skip_cmd(ctx):
        """Pula a música atual"""
        name = this_name()
        
        # Só responde se designado
        if not is_assigned_for_guild(ctx.guild.id):
            return
        
        player: wavelink.Player = ctx.guild.voice_client
        
        if not player or not player.playing:
            return await ctx.reply(
                embed=discord.Embed(description="❌ Nada tocando.", color=COLOR_ERROR)
            )
        
        await player.stop()
        print(f'[{name}] ⏭️ Skip solicitado em {ctx.guild.name}')
        return await ctx.reply(
            embed=discord.Embed(description="⏭️ Música pulada!", color=COLOR_SUCCESS)
        )
    
    @music_bot.command(name='stop')
    async def stop_cmd(ctx):
        """Para a música e limpa a fila"""
        name = this_name()
        
        # Só responde se designado
        if not is_assigned_for_guild(ctx.guild.id):
            return
        
        player: wavelink.Player = ctx.guild.voice_client
        
        if not player:
            return await ctx.reply(
                embed=discord.Embed(description="❌ Não estou em um canal de voz.", color=COLOR_ERROR)
            )
        
        queue_obj = get_bot_queue(ctx.guild.id)
        queue_obj.queue.clear()
        queue_obj.current = None
        queue_obj.bot_name = None
        
        mark_bot_free(name)
        
        await player.disconnect()
        print(f'[{name}] ⏹️ Stop e desconectado em {ctx.guild.name}')
        return await ctx.reply(
            embed=discord.Embed(description="⏹️ Parado e desconectado.", color=COLOR_SUCCESS)
        )
    
    return music_bot

async def start_music_bot(name, token):
    """Inicia um bot de música usando a factory"""
    try:
        if not token:
            print(f'❌ Token não configurado para {name}')
            return
        
        # Criar bot usando factory (evita closure bug)
        music_bot = create_music_bot(name, token)
        
        # Iniciar bot
        await music_bot.start(token)
        
    except Exception as e:
        print(f'❌ Erro ao iniciar {name}: {e}')
        import traceback
        traceback.print_exc()

async def start_all_bots():
    """Inicia o bot principal - SEM MÚSICA"""
    try:
        print('=' * 60)
        print(' INICIANDO CAOS BOT - MODERAÇÃO E VENDAS')
        print('=' * 60)
        
        # Verificar token principal
        if not TOKEN:
            print(' ERRO: DISCORD_TOKEN não encontrado!')
            exit(1)
        
        print(' Iniciando bot principal (CAOS Hub)...')
        
        @bot.event
        async def on_ready():
            print(f' [{bot.user}] está online!')
            print(f'  [{bot.user}] conectado em {len(bot.guilds)} servidor(es)')
            
            # Status personalizado
            activity = discord.Game("  O Hub dos sonhos...")
            await bot.change_presence(activity=activity)
            
            # Carregar dados
            load_warnings_data()
            load_role_config()
            load_welcome_config()
            
            # Sistema anti-hibernação
            if not keep_alive.is_running():
                keep_alive.start()
        
        await bot.start(TOKEN)
        
    except KeyboardInterrupt:
        print('\n Encerrando sistema...')
    except Exception as e:
        print(f' Erro crítico: {e}')
        traceback.print_exc()
        time.sleep(30)

if __name__ == '__main__':
    # Rodar todos os bots
    asyncio.run(start_all_bots())

# Sistema anti-hibernação já definido no início do arquivo

