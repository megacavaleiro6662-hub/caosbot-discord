"""
⚡ SISTEMA AUTOMÁTICO DE GANHO DE XP
Processa mensagens e dá XP
"""

import discord
from discord.ext import commands
from xp_database import xp_db
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Cache em memória para performance
xp_cache = defaultdict(dict)
last_xp_time = {}


async def process_xp_gain(message):
    """Processa ganho de XP ao enviar mensagem"""
    
    # Ignorar bots
    if message.author.bot:
        return
    
    # Ignorar DM
    if not message.guild:
        return
    
    guild_id = message.guild.id
    user_id = message.author.id
    
    # Pegar config
    config = xp_db.get_config(guild_id)
    
    # Sistema desativado?
    if not config.is_enabled:
        return
    
    # Verificar cooldown
    cache_key = f'{guild_id}_{user_id}'
    last_time = last_xp_time.get(cache_key, datetime.min)
    
    now = datetime.utcnow()
    if (now - last_time).total_seconds() < config.cooldown:
        return
    
    # Verificar se o canal está bloqueado
    blocked_channels = xp_db.get_blocked_channels(guild_id)
    if message.channel.id in blocked_channels:
        return
    
    # Verificar se o usuário tem cargo bloqueado
    blocked_roles = xp_db.get_blocked_roles(guild_id)
    user_role_ids = [r.id for r in message.author.roles]
    if any(role_id in blocked_roles for role_id in user_role_ids):
        return
    
    # Calcular XP base
    xp_amount = random.randint(config.min_xp, config.max_xp)
    
    # Aplicar multiplicadores de cargo
    multipliers = xp_db.get_multipliers(guild_id)
    for mult in multipliers:
        if mult.role_id in user_role_ids:
            xp_amount = int(xp_amount * mult.multiplier)
            break
    
    # Aplicar boost ativo
    boost = xp_db.get_active_boost(guild_id)
    if boost:
        xp_amount = int(xp_amount * boost.multiplier)
    
    # Adicionar XP
    old_level, new_level, total_xp = xp_db.add_xp(guild_id, user_id, xp_amount)
    
    # Atualizar cache de cooldown
    last_xp_time[cache_key] = now
    
    # Level up?
    if new_level > old_level:
        await handle_level_up(message, new_level, total_xp, config)


async def handle_level_up(message, new_level, total_xp, config):
    """Trata subida de nível"""
    
    guild = message.guild
    user = message.author
    
    # Pegar dados do nível
    levels = xp_db.get_levels(guild.id)
    level_data = None
    for lvl in levels:
        if lvl.level == new_level:
            level_data = lvl
            break
    
    if not level_data:
        return
    
    # Dar cargo
    role = guild.get_role(level_data.role_id)
    if role:
        try:
            # Modo de recompensa
            if config.reward_mode == 'replace':
                # Remover cargos anteriores
                for lvl in levels:
                    if lvl.level < new_level:
                        old_role = guild.get_role(lvl.role_id)
                        if old_role and old_role in user.roles:
                            await user.remove_roles(old_role)
            
            # Adicionar novo cargo
            if role not in user.roles:
                await user.add_roles(role)
        except:
            pass
    
    # Adicionar XP de recompensa (se tiver)
    if level_data.xp_reward > 0:
        xp_db.add_xp(guild.id, user.id, level_data.xp_reward)
    
    # Enviar anúncio
    await send_level_up_announcement(message, new_level, level_data, config)


async def send_level_up_announcement(message, new_level, level_data, config):
    """Envia anúncio de level up"""
    
    # Formatar mensagem
    msg_text = config.message_template.format(
        user=message.author.name,
        user_mention=message.author.mention,
        level=new_level,
        level_name=level_data.role_name,
        xp=xp_db.get_user_xp(message.guild.id, message.author.id).xp,
        guild_name=message.guild.name
    )
    
    channels_to_send = []
    
    # Canal atual
    if config.announce_current_channel:
        channels_to_send.append(message.channel)
    
    # Canal personalizado
    if config.announce_custom_channel and config.announce_channel_id:
        custom_channel = message.guild.get_channel(config.announce_channel_id)
        if custom_channel:
            channels_to_send.append(custom_channel)
    
    # Enviar mensagem
    for channel in channels_to_send:
        try:
            if config.message_type == 'embed':
                embed = discord.Embed(
                    title=f'🎉 Level Up!',
                    description=msg_text,
                    color=0x00ff00
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await channel.send(embed=embed)
            elif config.message_type == 'image':
                # TODO: Gerar imagem de level up
                await channel.send(msg_text)
            else:
                await channel.send(msg_text)
        except:
            pass
    
    # Mensagem direta
    if config.announce_dm:
        try:
            if config.message_type == 'embed':
                embed = discord.Embed(
                    title=f'🎉 Level Up em {message.guild.name}!',
                    description=msg_text,
                    color=0x00ff00
                )
                await message.author.send(embed=embed)
            else:
                await message.author.send(msg_text)
        except:
            pass


def setup_xp_system(bot):
    """Configura o sistema de XP no bot"""
    
    @bot.event
    async def on_message(message):
        """Hook para processar XP"""
        await process_xp_gain(message)
        await bot.process_commands(message)
    
    print('✅ Sistema de XP ativo!')
    return True


print('✅ XP System carregado!')
