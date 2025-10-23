"""
⭐ SISTEMA DE XP AUTOMÁTICO
Lógica de ganho de XP, levels, cooldown e anti-spam
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import asyncio
from xp_database import xp_db, XPUser

# ==================== CACHE DE XP (PERFORMANCE) ====================

class XPCache:
    """Cache em memória para evitar queries excessivas"""
    
    def __init__(self):
        self.cache = {}  # {(guild_id, user_id): {'xp': int, 'level': int, 'last_update': datetime}}
        self.cooldowns = {}  # {(guild_id, user_id): datetime}
    
    def get(self, guild_id, user_id):
        """Pega do cache"""
        return self.cache.get((guild_id, user_id))
    
    def set(self, guild_id, user_id, xp, level):
        """Salva no cache"""
        self.cache[(guild_id, user_id)] = {
            'xp': xp,
            'level': level,
            'last_update': datetime.utcnow()
        }
    
    def is_on_cooldown(self, guild_id, user_id, cooldown_seconds):
        """Verifica se está em cooldown"""
        key = (guild_id, user_id)
        if key in self.cooldowns:
            elapsed = (datetime.utcnow() - self.cooldowns[key]).total_seconds()
            return elapsed < cooldown_seconds
        return False
    
    def set_cooldown(self, guild_id, user_id):
        """Define cooldown"""
        self.cooldowns[(guild_id, user_id)] = datetime.utcnow()
    
    def clear(self):
        """Limpa cache"""
        self.cache.clear()
        self.cooldowns.clear()


xp_cache = XPCache()


# ==================== FUNÇÕES AUXILIARES ====================

def calculate_xp_for_level(level, levels_config):
    """Calcula XP necessário para um nível"""
    for level_data in levels_config:
        if level_data.level == level:
            return level_data.required_xp
    return 999999  # XP infinito se não encontrar


def get_next_level_xp(current_xp, levels_config):
    """Retorna XP necessário para o próximo nível"""
    for level_data in sorted(levels_config, key=lambda x: x.required_xp):
        if level_data.required_xp > current_xp:
            return level_data.required_xp
    return None  # Já está no level máximo


def calculate_level_from_xp(xp, levels_config):
    """Calcula o nível baseado no XP total"""
    current_level = 1
    for level_data in sorted(levels_config, key=lambda x: x.required_xp, reverse=True):
        if xp >= level_data.required_xp:
            current_level = level_data.level
            break
    return current_level


# ==================== SISTEMA DE XP ====================

class XPSystem:
    """Sistema completo de XP"""
    
    def __init__(self, bot):
        self.bot = bot
        self.last_messages = {}  # Anti-spam: {(guild_id, user_id): 'última mensagem'}
        
        # Task de sincronização cache → banco
        self.sync_task = self.bot.loop.create_task(self.sync_cache_to_db())
    
    async def sync_cache_to_db(self):
        """Sincroniza cache com banco de dados a cada 5 minutos"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await asyncio.sleep(300)  # 5 minutos
                
                print('🔄 Sincronizando cache de XP com banco de dados...')
                
                for (guild_id, user_id), data in xp_cache.cache.items():
                    try:
                        xp_db.update_user_xp(guild_id, user_id, data['xp'], data['level'])
                    except Exception as e:
                        print(f'❌ Erro ao sincronizar {user_id}: {e}')
                
                print('✅ Cache sincronizado!')
                
            except Exception as e:
                print(f'❌ Erro na sincronização: {e}')
                await asyncio.sleep(60)
    
    async def process_message(self, message):
        """Processa mensagem e dá XP se aplicável"""
        
        # Ignorar bots
        if message.author.bot:
            return
        
        # Ignorar DMs
        if not message.guild:
            return
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        # Pegar configuração do servidor
        config = xp_db.get_config(guild_id)
        
        # Sistema desativado?
        if not config.is_enabled:
            return
        
        # Verificar cooldown
        if xp_cache.is_on_cooldown(guild_id, user_id, config.cooldown):
            return
        
        # Anti-spam: ignorar mensagens repetidas
        last_msg = self.last_messages.get((guild_id, user_id))
        if last_msg == message.content:
            return
        self.last_messages[(guild_id, user_id)] = message.content
        
        # Ignorar mensagens muito curtas
        if len(message.content) < 3:
            return
        
        # Verificar se o canal está bloqueado
        if config.blocked_channels:
            blocked = [int(c) for c in config.blocked_channels.split(',') if c]
            if message.channel.id in blocked:
                return
        
        # Verificar se o usuário tem cargo bloqueado
        if config.blocked_roles:
            blocked_roles = [int(r) for r in config.blocked_roles.split(',') if r]
            user_role_ids = [role.id for role in message.author.roles]
            if any(role_id in blocked_roles for role_id in user_role_ids):
                return
        
        # Calcular XP a ganhar
        base_xp = random.randint(config.min_xp, config.max_xp)
        
        # Multiplicador por cargo
        multiplier = 1.0
        levels_config = xp_db.get_levels(guild_id)
        for level_data in levels_config:
            if level_data.role_id in user_role_ids:
                multiplier = max(multiplier, level_data.multiplier)
        
        # Boost ativo?
        boost = xp_db.get_active_boost(guild_id)
        if boost:
            multiplier *= boost.multiplier
        
        xp_to_add = int(base_xp * multiplier)
        
        # Pegar XP atual do usuário
        cached_data = xp_cache.get(guild_id, user_id)
        
        if cached_data:
            current_xp = cached_data['xp']
            current_level = cached_data['level']
        else:
            user_data = xp_db.get_user_xp(guild_id, user_id)
            if not user_data:
                user_data = xp_db.create_user_xp(guild_id, user_id)
            current_xp = user_data.xp
            current_level = user_data.level
        
        # Adicionar XP
        new_xp = current_xp + xp_to_add
        
        # Calcular novo nível
        new_level = calculate_level_from_xp(new_xp, levels_config)
        
        # Atualizar cache
        xp_cache.set(guild_id, user_id, new_xp, new_level)
        xp_cache.set_cooldown(guild_id, user_id)
        
        # LEVEL UP?
        if new_level > current_level:
            await self.handle_level_up(message, new_level, new_xp)
        
        # Salvar no banco (imediatamente para level ups, senão via sync)
        if new_level > current_level:
            xp_db.update_user_xp(guild_id, user_id, new_xp, new_level)
    
    async def handle_level_up(self, message, new_level, new_xp):
        """Gerencia level up: dar cargo, anunciar, etc"""
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        config = xp_db.get_config(guild_id)
        levels_config = xp_db.get_levels(guild_id)
        
        # Encontrar configuração do nível
        level_data = None
        for ld in levels_config:
            if ld.level == new_level:
                level_data = ld
                break
        
        if not level_data:
            return
        
        # Dar cargo
        try:
            role = message.guild.get_role(level_data.role_id)
            if role:
                # Modo: empilhar ou substituir?
                if config.reward_mode == 'replace':
                    # Remover cargos anteriores
                    for ld in levels_config:
                        if ld.level < new_level:
                            old_role = message.guild.get_role(ld.role_id)
                            if old_role and old_role in message.author.roles:
                                await message.author.remove_roles(old_role, reason=f'Level up para {new_level}')
                
                # Adicionar novo cargo
                if role not in message.author.roles:
                    await message.author.add_roles(role, reason=f'Level {new_level} alcançado!')
                    print(f'✅ {message.author} recebeu o cargo {role.name} (Level {new_level})')
        
        except Exception as e:
            print(f'❌ Erro ao dar cargo: {e}')
        
        # Anunciar level up
        await self.announce_level_up(message, new_level, level_data.role_name, new_xp)
    
    async def announce_level_up(self, message, new_level, level_name, new_xp):
        """Envia mensagem de level up"""
        
        guild_id = message.guild.id
        config = xp_db.get_config(guild_id)
        
        # Nenhum anúncio?
        if config.announce_mode == 'none':
            return
        
        # Substituir placeholders
        msg = config.message_template
        msg = msg.replace('{user}', message.author.name)
        msg = msg.replace('{user_mention}', message.author.mention)
        msg = msg.replace('{level}', str(new_level))
        msg = msg.replace('{level_name}', level_name)
        msg = msg.replace('{xp}', str(new_xp))
        msg = msg.replace('{guild_name}', message.guild.name)
        
        # Calcular XP do próximo nível
        levels_config = xp_db.get_levels(guild_id)
        next_xp = get_next_level_xp(new_xp, levels_config)
        if next_xp:
            msg = msg.replace('{next_level_xp}', str(next_xp))
        
        # Canal de destino
        target_channel = None
        
        if config.announce_mode == 'current':
            target_channel = message.channel
        elif config.announce_mode == 'custom' and config.announce_channel:
            target_channel = message.guild.get_channel(config.announce_channel)
        elif config.announce_mode == 'dm':
            target_channel = message.author
        
        if not target_channel:
            return
        
        try:
            # Tipo de mensagem
            if config.announce_type == 'text':
                await target_channel.send(msg)
            
            elif config.announce_type == 'embed':
                embed = discord.Embed(
                    title=f'🎉 Level Up!',
                    description=msg,
                    color=0x0066ff
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await target_channel.send(embed=embed)
            
            elif config.announce_type == 'image':
                # Gerar rank card (implementado em image_generator.py)
                from image_generator import generate_level_up_card
                
                card = await generate_level_up_card(
                    message.author,
                    new_level,
                    level_name,
                    new_xp,
                    config
                )
                
                if card:
                    await target_channel.send(file=card)
        
        except Exception as e:
            print(f'❌ Erro ao anunciar level up: {e}')
    
    def get_user_rank(self, guild_id, user_id):
        """Retorna a posição do usuário no ranking"""
        leaderboard = xp_db.get_leaderboard(guild_id, limit=999999)
        for idx, user in enumerate(leaderboard, start=1):
            if user.user_id == user_id:
                return idx
        return None


# ==================== INSTÂNCIA GLOBAL ====================

def setup_xp_system(bot):
    """Inicializa o sistema de XP"""
    xp_system = XPSystem(bot)
    
    @bot.event
    async def on_message(message):
        """Processa mensagens para XP"""
        await xp_system.process_message(message)
        await bot.process_commands(message)
    
    return xp_system


print('✅ Sistema de XP carregado!')
