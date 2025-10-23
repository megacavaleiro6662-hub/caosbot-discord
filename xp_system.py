"""
⚡ SISTEMA AUTOMÁTICO DE GANHO DE XP
Processa mensagens e aplica XP com multiplicadores/bloqueios
"""

import discord
from xp_database import xp_db
from datetime import datetime
import random
from collections import defaultdict

# Cache de cooldown
last_xp_time = {}


async def process_xp_gain(message):
    """Processa ganho de XP ao enviar mensagem"""
    
    if message.author.bot or not message.guild:
        return
    
    guild_id = message.guild.id
    user_id = message.author.id
    
    # Pegar config
    config = xp_db.get_config(guild_id)
    
    if not config.is_enabled:
        return
    
    # Cooldown
    cache_key = f'{guild_id}_{user_id}'
    last_time = last_xp_time.get(cache_key, datetime.min)
    now = datetime.utcnow()
    if (now - last_time).total_seconds() < config.cooldown:
        return
    
    # Canal bloqueado?
    blocked_channels = xp_db.get_blocked_channels(guild_id)
    if message.channel.id in blocked_channels:
        return
    
    # Cargo bloqueado?
    blocked_roles = xp_db.get_blocked_roles(guild_id)
    user_role_ids = [r.id for r in message.author.roles]
    if any(role_id in blocked_roles for role_id in user_role_ids):
        return
    
    # XP base
    xp_amount = random.randint(config.min_xp, config.max_xp)
    
    # Multiplicadores
    multipliers = xp_db.get_multipliers(guild_id)
    for mult in multipliers:
        if mult.role_id in user_role_ids:
            xp_amount = int(xp_amount * mult.multiplier)
            break
    
    # Adicionar XP
    old_level, new_level, total_xp = xp_db.add_xp(guild_id, user_id, xp_amount)
    last_xp_time[cache_key] = now
    
    # Level up?
    if new_level > old_level:
        await handle_level_up(message, new_level, config)


async def handle_level_up(message, new_level, config):
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
            if config.reward_mode == 'replace':
                # Remover cargos anteriores
                for lvl in levels:
                    if lvl.level < new_level:
                        old_role = guild.get_role(lvl.role_id)
                        if old_role and old_role in user.roles:
                            await user.remove_roles(old_role)
            
            # Adicionar novo
            if role not in user.roles:
                await user.add_roles(role)
        except:
            pass
    
    # Enviar anúncio
    await send_level_up_announcement(message, new_level, level_data, config)


async def send_level_up_announcement(message, new_level, level_data, config):
    """Envia anúncio de level up"""
    
    # Se TODOS estão desativados, não envia nada
    if config.announce_disabled:
        return
    
    # Formatar mensagem
    msg_text = config.message_template.format(
        user=message.author.name,
        user_mention=message.author.mention,
        level=new_level,
        level_name=level_data.role_name,
        xp=xp_db.get_user_xp(message.guild.id, message.author.id).xp,
        guild_name=message.guild.name
    )
    
    # Canal atual?
    if config.announce_current:
        try:
            if config.message_type == 'embed':
                embed = discord.Embed(title='🎉 Level Up!', description=msg_text, color=0x00ff00)
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(msg_text)
        except:
            pass
    
    # Canal personalizado?
    if config.announce_custom and config.announce_channel_id:
        custom_channel = message.guild.get_channel(config.announce_channel_id)
        if custom_channel:
            try:
                if config.message_type == 'embed':
                    embed = discord.Embed(title='🎉 Level Up!', description=msg_text, color=0x00ff00)
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    await custom_channel.send(embed=embed)
                else:
                    await custom_channel.send(msg_text)
            except:
                pass
    
    # Mensagem direta?
    if config.announce_dm:
        try:
            if config.message_type == 'embed':
                embed = discord.Embed(title=f'🎉 Level Up em {message.guild.name}!', description=msg_text, color=0x00ff00)
                await message.author.send(embed=embed)
            else:
                await message.author.send(msg_text)
        except:
            pass


def setup_xp_system(bot):
    """Configura hook de mensagens"""
    
    @bot.event
    async def on_message(message):
        await process_xp_gain(message)
        await bot.process_commands(message)
    
    print('✅ Sistema XP ativo!')
    return True


print('✅ XP System carregado!')
