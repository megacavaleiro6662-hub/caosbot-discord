# Bot Discord Caos - Python
# Arquivo principal do bot

import discord
from discord.ext import commands
import asyncio
import random
import time
import json
import os
from collections import defaultdict, deque
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import re

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Evento quando o bot fica online
@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    print(f'📊 Conectado em {len(bot.guilds)} servidor(es)')
    print(f'🤖 Bot ID: {bot.user.id}')
    
    # Carregar dados das advertências
    load_warnings_data()
    
    # Status do bot
    await bot.change_presence(
        activity=discord.Game(name="O Hub dos sonhos... 💭"),
        status=discord.Status.online
    )

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
    await ctx.reply(resposta)

@bot.command(name='comoesta')
async def comoesta_command(ctx, usuario: discord.Member = None):
    if usuario:
        await ctx.reply(f'{usuario.mention}, como você está hoje?')
    else:
        await ctx.reply('Como você está hoje?')

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
    await ctx.reply(f'💭 {topico}')

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
    await ctx.reply(pergunta)

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
    await ctx.reply(despedida)

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
spam_warnings = defaultdict(int)  # Avisos de spam por usuário

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
        
        # Remover todos os cargos de advertência
        cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
        cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
        cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
        
        roles_removidos = []
        
        if cargo_adv1 and cargo_adv1 in usuario.roles:
            await usuario.remove_roles(cargo_adv1)
            roles_removidos.append("ADV 1")
        if cargo_adv2 and cargo_adv2 in usuario.roles:
            await usuario.remove_roles(cargo_adv2)
            roles_removidos.append("ADV 2")
        if cargo_adv3 and cargo_adv3 in usuario.roles:
            await usuario.remove_roles(cargo_adv3)
            roles_removidos.append("ADV 3")
        
        # Resetar contador
        user_warnings[user_id] = 0
        
        embed = discord.Embed(
            title="🧹 TODAS ADVERTÊNCIAS REMOVIDAS",
            description=f"**{usuario.display_name}** teve TODAS as advertências removidas!",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"🧹 **Advertências anteriores:** {current_warnings}\n✨ **Cargos removidos:** {', '.join(roles_removidos) if roles_removidos else 'Nenhum'}\n🎉 Usuário com ficha limpa!",
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

@bot.command(name='seeadv')
@is_sub_moderator_or_higher()
async def seeadv_command(ctx):
    """Mostra TODOS os usuários com advertências de forma ULTRA DETALHADA"""
    
    # DEBUG: Verificar se os cargos existem
    cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
    cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
    cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
    
    print(f"🔍 DEBUG SEEADV:")
    print(f"📋 ADV_CARGO_1_ID: {ADV_CARGO_1_ID} -> {cargo_adv1.name if cargo_adv1 else 'NÃO ENCONTRADO'}")
    print(f"📋 ADV_CARGO_2_ID: {ADV_CARGO_2_ID} -> {cargo_adv2.name if cargo_adv2 else 'NÃO ENCONTRADO'}")
    print(f"📋 ADV_CARGO_3_ID: {ADV_CARGO_3_ID} -> {cargo_adv3.name if cargo_adv3 else 'NÃO ENCONTRADO'}")
    print(f"👥 Total de membros no servidor: {len(ctx.guild.members)}")
    print(f"💾 Dados salvos: {len(user_warnings)} usuários")
    
    # Listas para organizar usuários por nível
    adv1_users = []
    adv2_users = []
    adv3_users = []
    
    # Contador de debug
    members_checked = 0
    members_with_roles = 0
    
    # Verificar TODOS os usuários (incluindo dados salvos E cargos atuais)
    all_users_to_check = set()
    
    # 1. Adicionar usuários dos dados salvos
    for user_id, warnings in user_warnings.items():
        if warnings > 0:
            all_users_to_check.add(user_id)
            print(f"📊 Dados salvos: Usuário {user_id} tem {warnings} advertências")
    
    # 2. Adicionar usuários com cargos ADV
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        members_checked += 1
        
        # Verificar cargos ADV que o usuário POSSUI
        has_adv1 = cargo_adv1 and cargo_adv1 in member.roles
        has_adv2 = cargo_adv2 and cargo_adv2 in member.roles
        has_adv3 = cargo_adv3 and cargo_adv3 in member.roles
        
        # Se tem algum cargo ADV, adicionar à verificação
        if has_adv1 or has_adv2 or has_adv3:
            all_users_to_check.add(member.id)
            members_with_roles += 1
            print(f"🎯 {member.display_name}: ADV1={has_adv1}, ADV2={has_adv2}, ADV3={has_adv3}")
    
    print(f"📊 Membros verificados: {members_checked}")
    print(f"🎯 Membros com cargos ADV: {members_with_roles}")
    print(f"📋 Total de usuários para processar: {len(all_users_to_check)}")
    
    # Processar todos os usuários identificados
    for user_id in all_users_to_check:
        # Tentar obter o membro
        member = ctx.guild.get_member(user_id)
        if not member:
            print(f"⚠️ Usuário {user_id} não encontrado no servidor")
            continue
        
        # Verificar cargos ADV atuais
        has_adv1 = cargo_adv1 and cargo_adv1 in member.roles
        has_adv2 = cargo_adv2 and cargo_adv2 in member.roles
        has_adv3 = cargo_adv3 and cargo_adv3 in member.roles
        
        # Se não tem nenhum cargo ADV E não tem dados salvos, pular
        saved_warnings = user_warnings.get(user_id, 0)
        if not (has_adv1 or has_adv2 or has_adv3) and saved_warnings == 0:
            continue
        
        # Obter dados salvos do usuário
        warning_details = user_warnings_details.get(user_id, [])
        
        # Determinar nível mais alto (baseado em cargos OU dados salvos)
        highest_level = max(saved_warnings, 0)
        if has_adv3:
            highest_level = max(highest_level, 3)
        elif has_adv2:
            highest_level = max(highest_level, 2)
        elif has_adv1:
            highest_level = max(highest_level, 1)
        
        # Se não tem nível, pular
        if highest_level == 0:
            continue
        
        print(f"✅ Processando {member.display_name}: Nível {highest_level}, Cargos: ADV1={has_adv1}, ADV2={has_adv2}, ADV3={has_adv3}, Salvos={saved_warnings}")
        
        # Criar informações detalhadas do usuário
        user_data = {
            'member': member,
            'name': member.display_name,
            'id': user_id,
            'mention': member.mention,
            'highest_level': highest_level,
            'has_adv1': has_adv1,
            'has_adv2': has_adv2,
            'has_adv3': has_adv3,
            'saved_warnings': saved_warnings,
            'details': warning_details
        }
        
        # Adicionar à lista apropriada baseado no nível mais alto
        if highest_level >= 3:
            adv3_users.append(user_data)
            print(f"➡️ Adicionado à lista ADV 3: {member.display_name}")
        elif highest_level == 2:
            adv2_users.append(user_data)
            print(f"➡️ Adicionado à lista ADV 2: {member.display_name}")
        elif highest_level == 1:
            adv1_users.append(user_data)
            print(f"➡️ Adicionado à lista ADV 1: {member.display_name}")
    
    print(f"📊 RESULTADO FINAL:")
    print(f"🔴 ADV 3: {len(adv3_users)} usuários")
    print(f"🟠 ADV 2: {len(adv2_users)} usuários") 
    print(f"🟡 ADV 1: {len(adv1_users)} usuários")
    
    # Verificar se há usuários com advertências
    total_users = len(adv1_users) + len(adv2_users) + len(adv3_users)
    
    if total_users == 0:
        embed = discord.Embed(
            title="📊 RELATÓRIO DE ADVERTÊNCIAS",
            description="🎉 **SERVIDOR 100% LIMPO!**\n\n✨ Nenhum usuário possui cargos de advertência ativos.\n🧹 Todas as punições foram removidas ou expiradas.",
            color=0x00ff00
        )
        embed.add_field(
            name="📈 ESTATÍSTICAS",
            value="🟡 **ADV 1:** 0 usuários\n🟠 **ADV 2:** 0 usuários\n🔴 **ADV 3:** 0 usuários\n\n**TOTAL:** 0 usuários com advertências",
            inline=False
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    # Criar embed principal ULTRA DETALHADO
    embed = discord.Embed(
        title="📊 RELATÓRIO DE ADVERTÊNCIAS",
        description=f"**🔍 RESUMO DO SERVIDOR**\n\n📈 **Total:** {total_users} usuários com advertências\n🟡 **ADV 1:** {len(adv1_users)} • 🟠 **ADV 2:** {len(adv2_users)} • 🔴 **ADV 3:** {len(adv3_users)}\n\n📨 **Informações completas enviadas no privado de {ctx.author.display_name}**",
        color=0xff4444
    )
    
    # ========================================
    # ADV 3 - NÍVEL CRÍTICO
    # ========================================
    if adv3_users:
        adv3_text = ""
        for i, user in enumerate(adv3_users, 1):  # TODOS os usuários
            # Cargos ativos
            active_roles = []
            if user['has_adv1']:
                active_roles.append("🟡 ADV 1")
            if user['has_adv2']:
                active_roles.append("🟠 ADV 2")
            if user['has_adv3']:
                active_roles.append("🔴 ADV 3")
            
            # Última advertência
            last_warning = "Sem histórico disponível"
            moderator = "Sistema"
            timestamp = "Data desconhecida"
            
            if user['details']:
                last_detail = user['details'][-1]
                last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                moderator = last_detail.get('moderador', 'Moderador desconhecido')
                if 'timestamp' in last_detail:
                    timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
            
            adv3_text += f"**#{i} • {user['name']}**\n"
            adv3_text += f"🎯 **Cargos:** {' • '.join(active_roles) if active_roles else 'Apenas dados salvos'}\n"
            adv3_text += f"📝 **Motivo:** {last_warning[:40]}{'...' if len(last_warning) > 40 else ''}\n"
            adv3_text += f"👮 **Por:** {moderator} • ⏰ {timestamp}\n\n"
        
        embed.add_field(
            name=f"🔴 NÍVEL CRÍTICO - ADV 3 ({len(adv3_users)} usuários)",
            value=adv3_text[:1024] if adv3_text else "Nenhum usuário neste nível",
            inline=False
        )
    
    # ========================================
    # ADV 2 - NÍVEL ALTO
    # ========================================
    if adv2_users:
        adv2_text = ""
        for i, user in enumerate(adv2_users, 1):  # TODOS os usuários
            # Cargos ativos
            active_roles = []
            if user['has_adv1']:
                active_roles.append("🟡 ADV 1")
            if user['has_adv2']:
                active_roles.append("🟠 ADV 2")
            if user['has_adv3']:
                active_roles.append("🔴 ADV 3")
            
            # Última advertência
            last_warning = "Sem histórico disponível"
            moderator = "Sistema"
            timestamp = "Data desconhecida"
            
            if user['details']:
                last_detail = user['details'][-1]
                last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                moderator = last_detail.get('moderador', 'Moderador desconhecido')
                if 'timestamp' in last_detail:
                    timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
            
            adv2_text += f"**#{i} • {user['name']}**\n"
            adv2_text += f"🎯 **Cargos:** {' • '.join(active_roles) if active_roles else 'Apenas dados salvos'}\n"
            adv2_text += f"📝 **Motivo:** {last_warning[:40]}{'...' if len(last_warning) > 40 else ''}\n"
            adv2_text += f"👮 **Por:** {moderator} • ⏰ {timestamp}\n\n"
        
        embed.add_field(
            name=f"🟠 NÍVEL ALTO - ADV 2 ({len(adv2_users)} usuários)",
            value=adv2_text[:1024] if adv2_text else "Nenhum usuário neste nível",
            inline=False
        )
    
    # ========================================
    # ADV 1 - NÍVEL BAIXO
    # ========================================
    if adv1_users:
        adv1_text = ""
        for i, user in enumerate(adv1_users, 1):  # TODOS os usuários
            # Cargos ativos
            active_roles = []
            if user['has_adv1']:
                active_roles.append("🟡 ADV 1")
            if user['has_adv2']:
                active_roles.append("🟠 ADV 2")
            if user['has_adv3']:
                active_roles.append("🔴 ADV 3")
            
            # Última advertência
            last_warning = "Sem histórico disponível"
            moderator = "Sistema"
            timestamp = "Data desconhecida"
            
            if user['details']:
                last_detail = user['details'][-1]
                last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                moderator = last_detail.get('moderador', 'Moderador desconhecido')
                if 'timestamp' in last_detail:
                    timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
            
            adv1_text += f"**#{i} • {user['name']}**\n"
            adv1_text += f"🎯 **Cargos:** {' • '.join(active_roles) if active_roles else 'Apenas dados salvos'}\n"
            adv1_text += f"📝 **Motivo:** {last_warning[:40]}{'...' if len(last_warning) > 40 else ''}\n"
            adv1_text += f"👮 **Por:** {moderator} • ⏰ {timestamp}\n\n"
        
        embed.add_field(
            name=f"🟡 NÍVEL BAIXO - ADV 1 ({len(adv1_users)} usuários)",
            value=adv1_text[:1024] if adv1_text else "Nenhum usuário neste nível",
            inline=False
        )
    
    # ========================================
    # ESTATÍSTICAS FINAIS
    # ========================================
    embed.add_field(
        name="📈 ESTATÍSTICAS DETALHADAS",
        value=f"🎯 **Total geral:** {total_users} usuários com advertências\n\n🟡 **ADV 1 (Baixo):** {len(adv1_users)} usuários\n🟠 **ADV 2 (Alto):** {len(adv2_users)} usuários\n🔴 **ADV 3 (Crítico):** {len(adv3_users)} usuários\n\n📊 **Dados salvos:** {len([u for u in user_warnings.values() if u > 0])} registros\n🗂️ **Histórico completo:** {sum(len(details) for details in user_warnings_details.values())} advertências aplicadas",
        inline=False
    )
    
    # Verificar se alguma categoria foi truncada devido ao limite do Discord (1024 caracteres por field)
    truncated_categories = []
    if adv3_users and len(str(adv3_text)) >= 1024:
        truncated_categories.append("ADV 3")
    if adv2_users and len(str(adv2_text)) >= 1024:
        truncated_categories.append("ADV 2") 
    if adv1_users and len(str(adv1_text)) >= 1024:
        truncated_categories.append("ADV 1")
    
    if truncated_categories:
        embed.add_field(
            name="⚠️ AVISO DE TRUNCAMENTO",
            value=f"📋 As seguintes categorias foram **truncadas** devido ao limite do Discord:\n**{', '.join(truncated_categories)}**\n\n🔢 **Motivo:** Muitos usuários para exibir em uma única mensagem\n💡 **Solução:** Use `.debugadv` para ver lista completa ou remova algumas advertências",
            inline=False
        )
    
    embed.set_footer(text=f"📊 Sistema de Advertências • Consultado por {ctx.author.display_name} • Caos Hub")
    
    # PRIMEIRO: Enviar relatório no privado
    dm_success = False
    try:
        print(f"🔄 Tentando enviar DM para {ctx.author.display_name}...")
        
        # Testar se consegue enviar DM
        test_embed = discord.Embed(
            title="📨 RELATÓRIO COMPLETO DE ADVERTÊNCIAS",
            description=f"**🔍 SERVIDOR: {ctx.guild.name}**\n\n📊 **Estatísticas:**\n🎯 **Total:** {total_users} usuários\n🔴 **ADV 3:** {len(adv3_users)} • 🟠 **ADV 2:** {len(adv2_users)} • 🟡 **ADV 1:** {len(adv1_users)}",
            color=0xff4444
        )
        await ctx.author.send(embed=test_embed)
        dm_success = True
        print(f"✅ DM enviada com sucesso!")
        
    except discord.Forbidden:
        print(f"❌ DM bloqueada para {ctx.author.display_name}")
        dm_success = False
    except Exception as e:
        print(f"❌ Erro ao enviar DM: {e}")
        dm_success = False
    
    # SEGUNDO: Responder no canal com status
    if dm_success:
        embed.add_field(
            name="✅ RELATÓRIO ENVIADO",
            value=f"📨 **Lista completa enviada no privado!**\n📋 Verifique suas mensagens diretas para detalhes completos de todos os {total_users} usuários.",
            inline=False
        )
    else:
        embed.add_field(
            name="❌ ERRO NO ENVIO PRIVADO",
            value=f"🔒 **Não foi possível enviar no privado!**\n💡 **Solução:** Abra suas DMs e use o comando novamente\n📋 **Resumo:** {total_users} usuários com advertências no servidor",
            inline=False
        )
    
    await ctx.reply(embed=embed)
    
    # TERCEIRO: Se DM funcionou, enviar detalhes completos
    if dm_success and total_users > 0:
        
        try:
            # ========================================
            # ENVIAR DETALHES DE CADA CATEGORIA
            # ========================================
            
            # ADV 3 - Usuários críticos
            if adv3_users:
                for i, user in enumerate(adv3_users, 1):
                    # Cargos ativos
                    active_roles = []
                    if user['has_adv1']: active_roles.append("🟡 ADV 1")
                    if user['has_adv2']: active_roles.append("🟠 ADV 2")
                    if user['has_adv3']: active_roles.append("🔴 ADV 3")
                    
                    # Última advertência
                    last_warning = "Sem histórico disponível"
                    moderator = "Sistema"
                    timestamp = "Data desconhecida"
                    
                    if user['details']:
                        last_detail = user['details'][-1]
                        last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                        moderator = last_detail.get('moderador', 'Moderador desconhecido')
                        if 'timestamp' in last_detail:
                            timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
                    
                    user_embed = discord.Embed(
                        title=f"🔴 ADV 3 - USUÁRIO #{i}",
                        description=f"**{user['name']}**",
                        color=0xff0000
                    )
                    user_embed.add_field(name="🎯 Cargos Ativos", value=' • '.join(active_roles) if active_roles else 'Apenas dados salvos', inline=False)
                    user_embed.add_field(name="📝 Último Motivo", value=last_warning, inline=False)
                    user_embed.add_field(name="👮 Moderador", value=moderator, inline=True)
                    user_embed.add_field(name="⏰ Quando", value=timestamp, inline=True)
                    user_embed.add_field(name="🆔 ID", value=f"`{user['id']}`", inline=True)
                    user_embed.add_field(name="📊 Advertências Salvas", value=str(user['saved_warnings']), inline=True)
                    
                    await ctx.author.send(embed=user_embed)
                    await asyncio.sleep(0.3)  # Pausa para evitar rate limit
            
            # ADV 2 - Usuários de alto risco
            if adv2_users:
                for i, user in enumerate(adv2_users, 1):
                    # Cargos ativos
                    active_roles = []
                    if user['has_adv1']: active_roles.append("🟡 ADV 1")
                    if user['has_adv2']: active_roles.append("🟠 ADV 2")
                    if user['has_adv3']: active_roles.append("🔴 ADV 3")
                    
                    # Última advertência
                    last_warning = "Sem histórico disponível"
                    moderator = "Sistema"
                    timestamp = "Data desconhecida"
                    
                    if user['details']:
                        last_detail = user['details'][-1]
                        last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                        moderator = last_detail.get('moderador', 'Moderador desconhecido')
                        if 'timestamp' in last_detail:
                            timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
                    
                    user_embed = discord.Embed(
                        title=f"🟠 ADV 2 - USUÁRIO #{i}",
                        description=f"**{user['name']}**",
                        color=0xff8800
                    )
                    user_embed.add_field(name="🎯 Cargos Ativos", value=' • '.join(active_roles) if active_roles else 'Apenas dados salvos', inline=False)
                    user_embed.add_field(name="📝 Último Motivo", value=last_warning, inline=False)
                    user_embed.add_field(name="👮 Moderador", value=moderator, inline=True)
                    user_embed.add_field(name="⏰ Quando", value=timestamp, inline=True)
                    user_embed.add_field(name="🆔 ID", value=f"`{user['id']}`", inline=True)
                    user_embed.add_field(name="📊 Advertências Salvas", value=str(user['saved_warnings']), inline=True)
                    
                    await ctx.author.send(embed=user_embed)
                    await asyncio.sleep(0.3)
            
            # ADV 1 - Usuários de baixo risco
            if adv1_users:
                for i, user in enumerate(adv1_users, 1):
                    # Cargos ativos
                    active_roles = []
                    if user['has_adv1']: active_roles.append("🟡 ADV 1")
                    if user['has_adv2']: active_roles.append("🟠 ADV 2")
                    if user['has_adv3']: active_roles.append("🔴 ADV 3")
                    
                    # Última advertência
                    last_warning = "Sem histórico disponível"
                    moderator = "Sistema"
                    timestamp = "Data desconhecida"
                    
                    if user['details']:
                        last_detail = user['details'][-1]
                        last_warning = last_detail.get('motivo', 'Sem motivo especificado')
                        moderator = last_detail.get('moderador', 'Moderador desconhecido')
                        if 'timestamp' in last_detail:
                            timestamp = f"<t:{int(last_detail['timestamp'].timestamp())}:R>"
                    
                    user_embed = discord.Embed(
                        title=f"🟡 ADV 1 - USUÁRIO #{i}",
                        description=f"**{user['name']}**",
                        color=0xffdd00
                    )
                    user_embed.add_field(name="🎯 Cargos Ativos", value=' • '.join(active_roles) if active_roles else 'Apenas dados salvos', inline=False)
                    user_embed.add_field(name="📝 Último Motivo", value=last_warning, inline=False)
                    user_embed.add_field(name="👮 Moderador", value=moderator, inline=True)
                    user_embed.add_field(name="⏰ Quando", value=timestamp, inline=True)
                    user_embed.add_field(name="🆔 ID", value=f"`{user['id']}`", inline=True)
                    user_embed.add_field(name="📊 Advertências Salvas", value=str(user['saved_warnings']), inline=True)
                    
                    await ctx.author.send(embed=user_embed)
                    await asyncio.sleep(0.3)
            
            # Embed final
            final_embed = discord.Embed(
                title="📋 RELATÓRIO CONCLUÍDO",
                description=f"✅ **Relatório completo enviado!**\n\n📊 **Total:** {total_users} usuários processados\n🔴 **ADV 3:** {len(adv3_users)} • 🟠 **ADV 2:** {len(adv2_users)} • 🟡 **ADV 1:** {len(adv1_users)}\n\n💡 **Comandos úteis:**\n• `.radvallserver` - Limpar todas\n• `.radv @usuário` - Remover uma",
                color=0x00ff00
            )
            final_embed.set_footer(text=f"Relatório de {ctx.guild.name} • Gerado por {ctx.author.display_name}")
            await ctx.author.send(embed=final_embed)
            
            print(f"✅ Relatório completo enviado para {ctx.author.display_name}: {total_users} usuários")
            
        except Exception as e:
            print(f"❌ Erro ao enviar detalhes completos: {e}")
            error_embed = discord.Embed(
                title="❌ ERRO NO ENVIO DETALHADO",
                description=f"Houve um erro ao enviar os detalhes completos:\n```{str(e)}```",
                color=0xff0000
            )
            await ctx.author.send(embed=error_embed)

@seeadv_command.error
async def seeadv_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ Você precisa ser **Sub Moderador** ou ter permissões de moderação para usar este comando!")

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
async def mute_command(ctx, usuario: discord.Member = None, *, motivo="Sem motivo especificado"):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `.mute @usuário [motivo]`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se mutar!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode mutar este usuário!")
        return
    
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
        await usuario.add_roles(mute_role, reason=f"Mutado por {ctx.author} | Motivo: {motivo}")
        
        embed = discord.Embed(
            title="🔇 USUÁRIO MUTADO",
            description=f"**{usuario.display_name}** foi mutado indefinidamente!",
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
            value="Indefinido",
            inline=True
        )
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
    except discord.Forbidden:
        pass  # Não mostrar erro se a ação foi executada
    except Exception as e:
        await ctx.reply(f"❌ Erro ao mutar usuário: {e}")

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

@bot.command(name='radvallserver')
@commands.has_permissions(administrator=True)
async def radvallserver_command(ctx):
    """Remove todas as advertências de TODOS os usuários do servidor"""
    
    # Verificar se há usuários com advertências
    if not user_warnings or all(count == 0 for count in user_warnings.values()):
        embed = discord.Embed(
            title="ℹ️ SERVIDOR LIMPO",
            description="🎉 **Nenhum usuário possui advertências para remover!**\n\nO servidor já está limpo! ✨",
            color=0x00ff00
        )
        embed.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    # Confirmação de segurança
    embed_confirm = discord.Embed(
        title="⚠️ CONFIRMAÇÃO NECESSÁRIA",
        description="🚨 **ATENÇÃO!** Você está prestes a remover **TODAS** as advertências de **TODOS** os usuários do servidor!\n\n**Esta ação é IRREVERSÍVEL!**",
        color=0xff8c00
    )
    embed_confirm.add_field(
        name="📊 Usuários Afetados",
        value=f"**Total:** {len([u for u, c in user_warnings.items() if c > 0])} usuários",
        inline=True
    )
    embed_confirm.add_field(
        name="🔄 Para Confirmar",
        value="Digite `CONFIRMAR` em 30 segundos",
        inline=True
    )
    embed_confirm.set_footer(text="Sistema de Advertências • Caos Hub")
    
    await ctx.reply(embed=embed_confirm)
    
    # Aguardar confirmação
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.upper() == "CONFIRMAR"
    
    try:
        await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        embed_timeout = discord.Embed(
            title="⏰ TEMPO ESGOTADO",
            description="❌ Operação cancelada por timeout.\n\nNenhuma advertência foi removida.",
            color=0xff0000
        )
        await ctx.reply(embed=embed_timeout)
        return
    
    # Executar limpeza geral
    try:
        users_cleaned = []
        roles_removed_total = []
        
        # Obter cargos ADV
        cargo_adv1 = ctx.guild.get_role(ADV_CARGO_1_ID)
        cargo_adv2 = ctx.guild.get_role(ADV_CARGO_2_ID)
        cargo_adv3 = ctx.guild.get_role(ADV_CARGO_3_ID)
        
        print(f"🧹 Iniciando limpeza TOTAL do servidor...")
        print(f"📊 Membros no servidor: {len(ctx.guild.members)}")
        print(f"📋 Dados salvos antes da limpeza: {len(user_warnings)} usuários")
        
        # Processar TODOS os membros do servidor para remover cargos ADV
        members_processed = 0
        for member in ctx.guild.members:
            if member.bot:  # Pular bots
                continue
                
            members_processed += 1
            try:
                roles_removed = []
                user_id = member.id
                
                # Verificar e remover CADA cargo ADV individualmente
                if cargo_adv1 and cargo_adv1 in member.roles:
                    try:
                        await member.remove_roles(cargo_adv1, reason="🧹 LIMPEZA TOTAL - Remoção de ADV 1")
                        roles_removed.append("🟡 ADV 1")
                        print(f"✅ Removido ADV 1 de {member.display_name}")
                    except Exception as e:
                        print(f"❌ Erro ao remover ADV 1 de {member.display_name}: {e}")
                
                if cargo_adv2 and cargo_adv2 in member.roles:
                    try:
                        await member.remove_roles(cargo_adv2, reason="🧹 LIMPEZA TOTAL - Remoção de ADV 2")
                        roles_removed.append("🟠 ADV 2")
                        print(f"✅ Removido ADV 2 de {member.display_name}")
                    except Exception as e:
                        print(f"❌ Erro ao remover ADV 2 de {member.display_name}: {e}")
                
                if cargo_adv3 and cargo_adv3 in member.roles:
                    try:
                        await member.remove_roles(cargo_adv3, reason="🧹 LIMPEZA TOTAL - Remoção de ADV 3")
                        roles_removed.append("🔴 ADV 3")
                        print(f"✅ Removido ADV 3 de {member.display_name}")
                    except Exception as e:
                        print(f"❌ Erro ao remover ADV 3 de {member.display_name}: {e}")
                
                # Se removeu algum cargo, adicionar à lista
                if roles_removed:
                    warning_count = user_warnings.get(user_id, 0)
                    users_cleaned.append({
                        'name': member.display_name,
                        'id': user_id,
                        'warnings': warning_count,
                        'roles_removed': roles_removed
                    })
                    roles_removed_total.extend(roles_removed)
                    print(f"🎯 {member.display_name}: Removidos {len(roles_removed)} cargos")
                
            except Exception as e:
                print(f"❌ ERRO CRÍTICO ao processar {member.display_name}: {e}")
                continue
        
        print(f"📊 Membros processados: {members_processed}")
        print(f"🎯 Usuários limpos: {len(users_cleaned)}")
        print(f"🗑️ Cargos removidos: {len(roles_removed_total)}")
        
        # Limpar TODOS os dados de advertências
        user_warnings.clear()
        user_warnings_details.clear()
        
        # Salvar dados limpos
        save_warnings_data()
        
        # Criar embed de resultado ULTRA DETALHADO
        embed_result = discord.Embed(
            title="🧹 LIMPEZA TOTAL CONCLUÍDA COM SUCESSO!",
            description="✅ **OPERAÇÃO COMPLETA - SERVIDOR 100% LIMPO!**\n\n🎯 **Todas as advertências foram removidas sem exceção**\n🗑️ **Todos os cargos ADV foram eliminados**\n💾 **Todos os dados foram apagados**",
            color=0x00ff00
        )
        
        # Estatísticas detalhadas
        embed_result.add_field(
            name="📊 ESTATÍSTICAS DA OPERAÇÃO",
            value=f"👥 **Membros processados:** {members_processed}\n🎯 **Usuários limpos:** {len(users_cleaned)}\n🗑️ **Total de cargos removidos:** {len(roles_removed_total)}\n\n📋 **Dados apagados:** {len(user_warnings)} registros\n🗂️ **Histórico limpo:** {sum(len(details) for details in user_warnings_details.values())} advertências",
            inline=False
        )
        
        # Contagem por tipo de cargo
        adv1_count = len([r for r in roles_removed_total if "ADV 1" in r])
        adv2_count = len([r for r in roles_removed_total if "ADV 2" in r])
        adv3_count = len([r for r in roles_removed_total if "ADV 3" in r])
        
        embed_result.add_field(
            name="🎯 CARGOS REMOVIDOS POR TIPO",
            value=f"🟡 **ADV 1:** {adv1_count} cargos removidos\n🟠 **ADV 2:** {adv2_count} cargos removidos\n🔴 **ADV 3:** {adv3_count} cargos removidos\n\n**TOTAL GERAL:** {len(roles_removed_total)} cargos eliminados",
            inline=False
        )
        
        # Detalhes dos usuários (primeiros 8)
        if users_cleaned:
            users_text = ""
            for i, user_data in enumerate(users_cleaned[:8]):
                roles_text = " • ".join(user_data['roles_removed'])
                users_text += f"**#{i+1}** {user_data['name']}\n🗑️ Removidos: {roles_text}\n📊 Advertências salvas: {user_data['warnings']}\n\n"
            
            if len(users_cleaned) > 8:
                users_text += f"**... e mais {len(users_cleaned) - 8} usuários processados**"
            
            embed_result.add_field(
                name="👤 USUÁRIOS PROCESSADOS (Detalhes)",
                value=users_text[:1024],
                inline=False
            )
        
        embed_result.add_field(
            name="👮 MODERADOR",
            value=ctx.author.mention,
            inline=True
        )
        
        embed_result.add_field(
            name="⏰ EXECUTADO EM",
            value=f"<t:{int(time.time())}:F>",
            inline=True
        )
        
        embed_result.set_footer(text="Sistema de Advertências • Caos Hub")
        await ctx.reply(embed=embed_result)
        
        # Enviar log especial
        await send_adv_log(ctx, ctx.author, f"LIMPEZA GERAL: {len(users_cleaned)} usuários limpos", 0, "remocao")
        
    except Exception as e:
        embed_error = discord.Embed(
            title="❌ ERRO NA LIMPEZA",
            description=f"Ocorreu um erro durante a limpeza geral:\n```{str(e)}```",
            color=0xff0000
        )
        await ctx.reply(embed=embed_error)

@radvallserver_command.error
async def radvallserver_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

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
        
        await usuario.kick(reason=f"Expulso por {ctx.author} | Motivo: {motivo}")
        
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
async def timeout_command(ctx, usuario: discord.Member = None, tempo: int = 10, *, motivo="Sem motivo especificado"):
    if usuario is None:
        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Você precisa mencionar um usuário!\n\n**Uso:** `!timeout @usuário [tempo_minutos] [motivo]`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario == ctx.author:
        await ctx.reply("❌ Você não pode se silenciar!")
        return
    
    if usuario.top_role >= ctx.author.top_role:
        await ctx.reply("❌ Você não pode silenciar este usuário!")
        return
    
    if tempo > 1440:  # Máximo 24 horas
        tempo = 1440
    
    try:
        timeout_duration = discord.utils.utcnow() + discord.timedelta(minutes=tempo)
        
        embed = discord.Embed(
            title="🔇 USUÁRIO SILENCIADO",
            description=f"**{usuario.display_name}** foi silenciado!",
            color=0xffa500
        )
        embed.add_field(
            name="⏰ Duração",
            value=f"`{tempo} minutos`",
            inline=True
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
        embed.set_footer(text="Sistema de Moderação • Caos Hub")
        await ctx.reply(embed=embed)
        
        await usuario.timeout(timeout_duration, reason=f"Timeout por {ctx.author} | Motivo: {motivo}")
        
    except discord.Forbidden:
        pass  # Não mostrar erro se a ação foi executada
    except Exception as e:
        await ctx.reply(f"❌ Erro ao silenciar usuário: {e}")

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

# ========================================
# SISTEMAS DE PROTEÇÃO AUTOMÁTICA
# ========================================

async def auto_moderate(message, violation_type, details=""):
    """Sistema automático de moderação"""
    user_id = message.author.id
    
    # Incrementar avisos de spam
    spam_warnings[user_id] += 1
    current_warnings = spam_warnings[user_id]
    
    # Deletar mensagem
    try:
        await message.delete()
    except:
        pass
    
    # Determinar punição baseada nos avisos
    if current_warnings == 1:
        # Primeiro aviso - apenas aviso
        embed = discord.Embed(
            title="⚠️ AVISO AUTOMÁTICO",
            description=f"**{message.author.display_name}**, cuidado com {violation_type}!",
            color=0xffff00
        )
        embed.add_field(
            name="📋 Detalhes",
            value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Avisos:** {current_warnings}/3",
            inline=False
        )
        embed.set_footer(text="Sistema de Proteção Automática • Caos Hub")
        
        msg = await message.channel.send(embed=embed)
        await asyncio.sleep(5)
        await msg.delete()
        
    elif current_warnings == 2:
        # Segundo aviso - timeout 5 minutos
        try:
            timeout_duration = discord.utils.utcnow() + discord.timedelta(minutes=5)
            await message.author.timeout(timeout_duration, reason=f"Auto-moderação: {violation_type}")
            
            embed = discord.Embed(
                title="🔇 TIMEOUT AUTOMÁTICO",
                description=f"**{message.author.display_name}** foi silenciado por 5 minutos!",
                color=0xff8c00
            )
            embed.add_field(
                name="📋 Detalhes",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Avisos:** {current_warnings}/3\n**Duração:** 5 minutos",
                inline=False
            )
            embed.set_footer(text="Sistema de Proteção Automática • Caos Hub")
            
            await message.channel.send(embed=embed)
        except:
            pass
            
    elif current_warnings >= 3:
        # Terceiro aviso - aplicar ADV 1
        try:
            # Aplicar advertência automática
            if user_id not in user_warnings:
                user_warnings[user_id] = 0
            
            user_warnings[user_id] += 1
            warning_count = user_warnings[user_id]
            
            # Aplicar cargo ADV 1
            guild = message.guild
            cargo = guild.get_role(ADV_CARGO_1_ID)
            if cargo:
                await message.author.add_roles(cargo)
            
            embed = discord.Embed(
                title="🚨 ADVERTÊNCIA AUTOMÁTICA",
                description=f"**{message.author.display_name}** recebeu ADV 1 por violações repetidas!",
                color=0xff0000
            )
            embed.add_field(
                name="📋 Detalhes",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Advertência:** ADV {warning_count}\n**Motivo:** Violações automáticas repetidas",
                inline=False
            )
            embed.set_footer(text="Sistema de Proteção Automática • Caos Hub")
            
            await message.channel.send(embed=embed)
            
            # Reset avisos de spam após aplicar advertência
            spam_warnings[user_id] = 0
            
        except:
            pass

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
            name="📊 `.seeadv`",
            value="**Mostra** todos usuários com advertências\n*Lista completa com detalhes*",
            inline=False
        )
        
        embed.add_field(
            name="🧹 `.radvallserver`",
            value="**LIMPA** todas advertências do servidor\n*⚠️ APENAS ADMINISTRADORES*",
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
            name="📊 `.seeadv`",
            value="**Lista** todos usuários com advertências\n*Relatório completo e detalhado*",
            inline=False
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
    await ctx.reply(f'😄 {piada}')

@bot.command(name='escolher')
async def escolher_command(ctx, *, opcoes):
    lista_opcoes = [opcao.strip() for opcao in opcoes.split(',')]
    if len(lista_opcoes) < 2:
        await ctx.reply('Preciso de pelo menos 2 opções separadas por vírgula!')
        return
    
    escolha = random.choice(lista_opcoes)
    await ctx.reply(f'🎲 Eu escolho: **{escolha}**!')

# ========================================
# RESPOSTAS AUTOMÁTICAS E PROTEÇÕES
# ========================================

@bot.event
async def on_message(message):
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
    # SISTEMA ANTI-SPAM
    # ========================================
    
    # Adicionar mensagem ao histórico
    message_history[user_id].append(content.lower())
    user_message_times[user_id].append(current_time)
    
    # Verificar spam (mensagens idênticas)
    if len(message_history[user_id]) >= 3:
        recent_messages = list(message_history[user_id])[-3:]
        if len(set(recent_messages)) == 1:  # Todas as mensagens são iguais
            await auto_moderate(message, "spam de mensagens idênticas", f"Enviou 3 mensagens iguais: '{content[:50]}...'")
            return
    
    # ========================================
    # SISTEMA ANTI-FLOOD
    # ========================================
    
    # Verificar flood (muitas mensagens em pouco tempo)
    if len(user_message_times[user_id]) >= 5:
        recent_times = list(user_message_times[user_id])[-5:]
        time_diff = recent_times[-1] - recent_times[0]
        
        if time_diff < 10:  # 5 mensagens em menos de 10 segundos
            await auto_moderate(message, "flood de mensagens", f"Enviou 5 mensagens em {time_diff:.1f} segundos")
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
                await auto_moderate(message, "excesso de maiúsculas", f"Mensagem com {caps_percentage:.1f}% em maiúsculas")
                return
    
    # ========================================
    # SISTEMA ANTI-MENTION SPAM
    # ========================================
    
    # Verificar spam de menções
    mention_count = len(message.mentions) + len(message.role_mentions)
    if mention_count > 5:
        await auto_moderate(message, "spam de menções", f"Mencionou {mention_count} usuários/cargos")
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
        await auto_moderate(message, "spam de emojis", f"Enviou {total_emojis} emojis em uma mensagem")
        return
    
    # ========================================
    # SISTEMA ANTI-LINK SPAM
    # ========================================
    
    # Verificar links suspeitos (muitos links)
    link_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.br', '.gg']
    link_count = sum(content.lower().count(pattern) for pattern in link_patterns)
    
    if link_count > 3:
        await auto_moderate(message, "spam de links", f"Enviou {link_count} links em uma mensagem")
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
# CONFIGURAÇÃO E INICIALIZAÇÃO
# ========================================

# Servidor HTTP simples para o Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot Discord Caos - Online!')
    
    def log_message(self, format, *args):
        pass  # Silencia logs HTTP

def start_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'🌐 Servidor HTTP iniciado na porta {port}')
    server.serve_forever()

# Token do bot (usando variável de ambiente para segurança)
TOKEN = os.getenv('DISCORD_TOKEN')

# Iniciar o bot
if __name__ == '__main__':
    try:
        print('🚀 Iniciando bot Discord Caos...')
        print(f'🔑 Token configurado: {"✅ Sim" if TOKEN else "❌ Não"}')
        
        if not TOKEN:
            print('❌ ERRO: Variável DISCORD_TOKEN não encontrada!')
            print('💡 Configure a variável de ambiente DISCORD_TOKEN no Render')
            exit(1)
        
        # Inicia servidor HTTP em thread separada
        http_thread = Thread(target=start_http_server, daemon=True)
        http_thread.start()
        
        # Inicia o bot Discord
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('❌ Erro de login: Token inválido!')
        print('🔑 Verifique se a variável DISCORD_TOKEN está correta!')
    except Exception as e:
        print(f'❌ Erro ao iniciar o bot: {e}')
        print('🔧 Verifique as configurações e tente novamente!')
