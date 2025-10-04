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
# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# ========================================
# SISTEMA ANTI-HIBERNAÇÃO (100% GRATUITO)
# ========================================

@tasks.loop(minutes=10)  # Ping a cada 10 minutos
async def keep_alive():
    """Mantém o bot sempre ativo - impede hibernação do Render"""
    try:
        # Fazer requisição HTTP para manter ativo
        async with aiohttp.ClientSession() as session:
            # Ping para um serviço público gratuito
            async with session.get('https://httpbin.org/get', timeout=30) as response:
                if response.status == 200:
                    current_time = datetime.now().strftime('%H:%M:%S')
                    print(f'❤️ [{current_time}] Bot mantido ativo - Sistema anti-hibernação OK!')
                else:
                    print(f'⚠️ Ping falhou - Status: {response.status}')
    except asyncio.TimeoutError:
        print('⚠️ Timeout no ping - mas bot continua ativo')
    except Exception as e:
        print(f'❌ Erro no sistema anti-hibernação: {e}')
        print('🔄 Bot continua funcionando normalmente')

@keep_alive.before_loop
async def before_keep_alive():
    """Aguarda o bot estar pronto antes de iniciar o sistema"""
    await bot.wait_until_ready()
    print('✅ Bot pronto! Iniciando sistema anti-hibernação...')

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
    
    # INICIAR SISTEMA ANTI-HIBERNAÇÃO
    if not keep_alive.is_running():
        keep_alive.start()
        print('🔄 Sistema anti-hibernação ATIVADO! Bot ficará online 24/7')
    
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
            description="Você precisa mencionar um usuário!\n\n**Uso:** `.timeout @usuário [tempo_minutos] [motivo]`",
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
    
    # Verificar se já está em timeout
    if usuario.timed_out_until and usuario.timed_out_until > discord.utils.utcnow():
        await ctx.reply("❌ Este usuário já está em timeout!")
        return
    
    # Limitar tempo (Discord permite máximo 28 dias = 40320 minutos)
    if tempo > 40320:
        tempo = 40320
    elif tempo < 1:
        tempo = 1
    
    try:
        # Calcular duração do timeout
        timeout_duration = discord.utils.utcnow() + discord.timedelta(minutes=tempo)
        
        # Aplicar timeout PRIMEIRO
        await usuario.timeout(timeout_duration, reason=f"Timeout por {ctx.author.display_name} | Motivo: {motivo}")
        
        # Depois mostrar confirmação
        embed = discord.Embed(
            title="🔇 USUÁRIO SILENCIADO",
            description=f"**{usuario.display_name}** foi silenciado com sucesso!",
            color=0xffa500
        )
        embed.add_field(
            name="⏰ Duração",
            value=f"`{tempo} minutos`",
            inline=True
        )
        embed.add_field(
            name="📅 Expira em",
            value=f"<t:{int(timeout_duration.timestamp())}:F>",
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

# ========================================
# SISTEMAS DE PROTEÇÃO AUTOMÁTICA
# ========================================

async def auto_moderate_progressive(message, violation_type, details=""):
    """Sistema automático de moderação PROGRESSIVO - Conforme solicitado pelo usuário"""
    user_id = message.author.id
    
    # Deletar mensagem
    try:
        await message.delete()
    except:
        pass
    
    # Incrementar avisos de spam
    spam_warnings[user_id] += 1
    current_warnings = spam_warnings[user_id]
    
    # Sistema: 5 msgs → aviso, 4 msgs → aviso, 3 msgs → ADV
    if current_warnings == 1:
        # PRIMEIRO AVISO (5 mensagens) - SEM castigo
        try:
            embed = discord.Embed(
                title="⚠️ PRIMEIRO AVISO - SPAM DETECTADO",
                description=f"Você foi detectado fazendo spam no servidor **{message.guild.name}**!",
                color=0xffff00
            )
            embed.add_field(
                name="📋 Detalhes",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Canal:** {message.channel.mention}\n**Próximo:** Segundo aviso (4 mensagens)",
                inline=False
            )
            embed.add_field(
                name="⚠️ Atenção",
                value="Se continuar, você receberá **ADV 1** e **timeout de 1 minuto**!",
                inline=False
            )
            embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
            
            # Enviar DM
            try:
                await message.author.send(embed=embed)
            except:
                pass
            
            # Enviar mensagem no canal (só a pessoa vê) - usando delete_after
            try:
                msg = await message.channel.send(f"{message.author.mention} ⚠️ **Primeiro aviso de spam!** Verifique sua DM.", delete_after=5)
            except:
                pass
        except:
            pass
        
    elif current_warnings == 2:
        # SEGUNDO AVISO (4 mensagens) - SEM castigo
        try:
            embed = discord.Embed(
                title="🚨 SEGUNDO AVISO - ÚLTIMA CHANCE",
                description=f"**ATENÇÃO!** Você está prestes a receber uma advertência no servidor **{message.guild.name}**!",
                color=0xff8c00
            )
            embed.add_field(
                name="📋 Detalhes",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Canal:** {message.channel.mention}\n**Próximo:** ADV 1 + Timeout de 1 minuto (3 mensagens)",
                inline=False
            )
            embed.add_field(
                name="🚨 ÚLTIMA CHANCE",
                value="Se enviar mais spam, você receberá **ADV 1** automaticamente e ficará **1 minuto em timeout**!",
                inline=False
            )
            embed.set_footer(text="Sistema Anti-Spam • Caos Hub")
            
            # Enviar DM
            try:
                await message.author.send(embed=embed)
            except:
                pass
            
            # Enviar mensagem no canal (só a pessoa vê)
            try:
                msg = await message.channel.send(f"{message.author.mention} 🚨 **ÚLTIMO AVISO!** Próximo spam = ADV 1. Verifique sua DM.", delete_after=5)
            except:
                pass
        except:
            pass
            
    elif current_warnings >= 3:
        # TERCEIRA VIOLAÇÃO - APLICAR ADV
        try:
            # Aplicar advertência automática
            if user_id not in user_warnings:
                user_warnings[user_id] = 0
            
            user_warnings[user_id] += 1
            warning_count = user_warnings[user_id]
            
            # Determinar cargo baseado no nível de advertência
            if warning_count == 1:
                # ADV 1
                cargo = message.guild.get_role(ADV_CARGO_1_ID)
                adv_level = "ADV 1"
                color = 0xffff00
                next_punishment = "ADV 2"
            elif warning_count == 2:
                # ADV 2 (remover ADV 1)
                cargo_antigo = message.guild.get_role(ADV_CARGO_1_ID)
                if cargo_antigo and cargo_antigo in message.author.roles:
                    await message.author.remove_roles(cargo_antigo)
                cargo = message.guild.get_role(ADV_CARGO_2_ID)
                adv_level = "ADV 2"
                color = 0xff8c00
                next_punishment = "ADV 3 + BAN"
            else:
                # ADV 3 + BAN (remover cargos anteriores)
                cargo_adv1 = message.guild.get_role(ADV_CARGO_1_ID)
                cargo_adv2 = message.guild.get_role(ADV_CARGO_2_ID)
                if cargo_adv1 and cargo_adv1 in message.author.roles:
                    await message.author.remove_roles(cargo_adv1)
                if cargo_adv2 and cargo_adv2 in message.author.roles:
                    await message.author.remove_roles(cargo_adv2)
                cargo = message.guild.get_role(ADV_CARGO_3_ID)
                adv_level = "ADV 3"
                color = 0xff0000
                next_punishment = "BANIMENTO"
            
            # Aplicar cargo
            if cargo:
                await message.author.add_roles(cargo)
            
            # APLICAR TIMEOUT DE 1 MINUTO quando levar ADV
            try:
                timeout_duration = discord.utils.utcnow() + discord.timedelta(minutes=1)
                await message.author.timeout(timeout_duration, reason=f"{adv_level} - Spam automático")
            except Exception as timeout_error:
                print(f"Erro ao aplicar timeout: {timeout_error}")
            
            embed = discord.Embed(
                title=f"🚨 {adv_level.upper()} APLICADA AUTOMATICAMENTE",
                description=f"**{message.author.display_name}** recebeu {adv_level} por spam repetido!",
                color=color
            )
            embed.add_field(
                name="📋 Detalhes da Punição",
                value=f"**Violação:** {violation_type}\n**Detalhes:** {details}\n**Advertência:** {adv_level}\n**Timeout:** 1 minuto\n**Próxima punição:** {next_punishment}",
                inline=False
            )
            embed.set_footer(text="Sistema Anti-Spam Automático • Caos Hub")
            
            await message.channel.send(embed=embed)
            
            # Se chegou no ADV 3, banir IMEDIATAMENTE
            if warning_count >= 3:
                await message.author.ban(reason="ADV 3 - Ban automático por spam repetido")
                user_warnings[user_id] = 0  # Reset após ban
                
                ban_embed = discord.Embed(
                    title="🔨 USUÁRIO BANIDO AUTOMATICAMENTE",
                    description=f"**{message.author.display_name}** foi banido por atingir ADV 3!",
                    color=0x000000
                )
                await message.channel.send(embed=ban_embed)
            
            # RESETAR avisos de spam após aplicar ADV (começa do zero)
            spam_warnings[user_id] = 0
            
            # Salvar dados
            save_warnings_data()
            
        except Exception as e:
            print(f"Erro na moderação automática: {e}")

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
            await auto_moderate_progressive(message, "spam de mensagens idênticas", f"Enviou 3 mensagens iguais: '{content[:50]}...'")
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
            await auto_moderate_progressive(message, "flood de mensagens", f"Enviou {flood_limit} mensagens em {time_diff:.1f} segundos")
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
                await auto_moderate_progressive(message, "excesso de maiúsculas", f"Mensagem com {caps_percentage:.1f}% em maiúsculas")
                return
    
    # ========================================
    # SISTEMA ANTI-MENTION SPAM
    # ========================================
    
    # Verificar spam de menções
    mention_count = len(message.mentions) + len(message.role_mentions)
    if mention_count > 5:
        await auto_moderate_progressive(message, "spam de menções", f"Mencionou {mention_count} usuários/cargos")
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
        await auto_moderate_progressive(message, "spam de emojis", f"Enviou {total_emojis} emojis em uma mensagem")
        return
    
    # ========================================
    # SISTEMA ANTI-LINK SPAM
    # ========================================
    
    # Verificar links suspeitos (muitos links)
    link_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.br', '.gg']
    link_count = sum(content.lower().count(pattern) for pattern in link_patterns)
    
    if link_count > 3:
        await auto_moderate_progressive(message, "spam de links", f"Enviou {link_count} links em uma mensagem")
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
    """SISTEMA NOVO - Adiciona cargo com hierarquia automática e prefixo"""
    
    # Verificar argumentos
    if not cargo or not usuario:
        embed = discord.Embed(
            title="❌ Uso Incorreto",
            description="Use: `.addrole @cargo @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    # Verificar se usuário já tem o cargo
    if cargo in usuario.roles:
        embed = discord.Embed(
            title="⚠️ Cargo Já Possui",
            description=f"**{usuario.display_name}** já possui o cargo **{cargo.name}**!",
            color=0xffaa00
        )
        embed.add_field(
            name="📋 Informação",
            value=f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo.mention}",
            inline=False
        )
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        await ctx.reply(embed=embed)
        return
    
    try:
        # Definir hierarquia dos cargos (maior = mais importante)
        HIERARCHY = {
            1365633918593794079: 4,  # ADM - mais alto
            1365634226254254150: 3,  # STF
            1365633102973763595: 2,  # MOD  
            1365631940434333748: 1   # SBM - mais baixo
        }
        
        # 1. REMOVER cargos conflitantes PRIMEIRO
        removed_roles = []
        if cargo.id in HIERARCHY:
            for role in list(usuario.roles):
                if role.id in HIERARCHY and role.id != cargo.id:
                    await usuario.remove_roles(role)
                    removed_roles.append(role.name)
        
        # 2. ADICIONAR o novo cargo
        await usuario.add_roles(cargo)
        
        # 3. ATUALIZAR nickname se cargo tem prefixo
        nickname_msg = ""
        if cargo.id in CARGO_PREFIXES:
            # Obter nome limpo (sem prefixos)
            clean_name = usuario.display_name
            for prefix in CARGO_PREFIXES.values():
                if clean_name.startswith(prefix + " "):
                    clean_name = clean_name[len(prefix + " "):]
                    break
            
            # Aplicar novo prefixo
            new_nickname = f"{CARGO_PREFIXES[cargo.id]} {clean_name}"
            
            # Limitar tamanho
            if len(new_nickname) > 32:
                max_length = 32 - len(CARGO_PREFIXES[cargo.id]) - 1
                clean_name = clean_name[:max_length]
                new_nickname = f"{CARGO_PREFIXES[cargo.id]} {clean_name}"
            
            await usuario.edit(nick=new_nickname)
            nickname_msg = f"\n🏷️ **Nickname:** `{new_nickname}`"
        
        # 4. EMBED de sucesso (ÚNICA MENSAGEM)
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
        embed = discord.Embed(
            title="❌ ERRO",
            description=f"Erro ao adicionar cargo: {e}",
            color=0xff0000
        )
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
    """SISTEMA NOVO - Remove cargo e restaura nickname com hierarquia"""
    
    # Verificar argumentos
    if not cargo or not usuario:
        embed = discord.Embed(
            title="❌ Uso Incorreto", 
            description="Use: `.removerole @cargo @usuário`",
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    # Verificar se usuário tem o cargo
    if cargo not in usuario.roles:
        embed = discord.Embed(
            title="⚠️ Cargo Não Possui",
            description=f"**{usuario.display_name}** não possui **{cargo.name}**!",
            color=0xffaa00
        )
        await ctx.reply(embed=embed)
        return
    
    try:
        # Definir hierarquia dos cargos
        HIERARCHY = {
            1365633918593794079: 4,  # ADM
            1365634226254254150: 3,  # STF
            1365633102973763595: 2,  # MOD  
            1365631940434333748: 1   # SBM
        }
        
        # 1. REMOVER o cargo PRIMEIRO
        await usuario.remove_roles(cargo)
        
        # 2. AGUARDAR para garantir que o cargo foi removido
        await asyncio.sleep(0.3)
        
        # 3. RECARREGAR o membro para pegar cargos atualizados
        usuario = await ctx.guild.fetch_member(usuario.id)
        
        # 4. RESTAURAR nickname baseado na hierarquia
        nickname_msg = ""
        if cargo.id in CARGO_PREFIXES:
            # Obter nome limpo (sem QUALQUER prefixo)
            clean_name = usuario.display_name
            for prefix in CARGO_PREFIXES.values():
                if clean_name.startswith(prefix + " "):
                    clean_name = clean_name[len(prefix + " "):]
                    break
            
            # Verificar se ainda tem outros cargos com prefixo
            highest_role = None
            highest_level = 0
            
            for role in usuario.roles:
                if role.id in HIERARCHY and role.id in CARGO_PREFIXES:
                    if HIERARCHY[role.id] > highest_level:
                        highest_level = HIERARCHY[role.id]
                        highest_role = role
            
            if highest_role:
                # Aplicar prefixo do cargo de maior hierarquia restante
                new_nickname = f"{CARGO_PREFIXES[highest_role.id]} {clean_name}"
                await usuario.edit(nick=new_nickname)
                nickname_msg = f"\n🏷️ **Nickname atualizado:** `{new_nickname}`"
            else:
                # NÃO TEM MAIS CARGOS COM PREFIXO - RESTAURAR NOME LIMPO
                await usuario.edit(nick=clean_name)
                nickname_msg = f"\n🏷️ **Nickname restaurado:** `{clean_name}`"
        
        # 5. EMBED de sucesso (ÚNICA MENSAGEM)
        embed = discord.Embed(
            title="✅ CARGO REMOVIDO",
            description=f"**{cargo.name}** foi removido de **{usuario.display_name}**!",
            color=0xff4444
        )
        
        details = f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo.mention}\n**Moderador:** {ctx.author.mention}"
        details += nickname_msg
        
        embed.add_field(name="📋 Detalhes", value=details, inline=False)
        embed.set_footer(text="Sistema de Cargos • Caos Hub")
        
        await ctx.reply(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ ERRO",
            description=f"Erro ao remover cargo: {e}",
            color=0xff0000
        )
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
        print(f'❌ Erro crítico: {e}')
        print('🔄 Reiniciando em 30 segundos...')
        time.sleep(30)

# Sistema anti-hibernação já definido no início do arquivo

