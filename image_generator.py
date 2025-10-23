"""
🎨 GERADOR DE IMAGENS COM PILLOW
Rank cards e leaderboards em tempo real
"""

import discord
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
from xp_database import xp_db

CARD_WIDTH = 800
CARD_HEIGHT = 250
AVATAR_SIZE = 150


async def download_avatar(url):
    """Baixa avatar do Discord"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return Image.open(io.BytesIO(data))
    except:
        pass
    return None


def hex_to_rgb(hex_color):
    """Converte hex para RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def make_circular(img, size):
    """Faz imagem circular"""
    img = img.resize((size, size))
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    return output


async def generate_rank_card(member, guild_id):
    """Gera rank card do usuário"""
    
    try:
        user_data = xp_db.get_user_xp(guild_id, member.id)
        if not user_data:
            return None
        
        # Canvas
        img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), (26, 26, 46))
        draw = ImageDraw.Draw(img)
        
        # Avatar
        avatar = await download_avatar(member.display_avatar.url)
        if avatar:
            avatar = make_circular(avatar, AVATAR_SIZE)
            img.paste(avatar, (30, (CARD_HEIGHT - AVATAR_SIZE) // 2), avatar)
        
        # Fontes
        try:
            font_large = ImageFont.truetype('arial.ttf', 48)
            font_medium = ImageFont.truetype('arial.ttf', 32)
            font_small = ImageFont.truetype('arial.ttf', 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Nome
        username = member.name if len(member.name) <= 20 else member.name[:17] + '...'
        draw.text((210, 40), username, font=font_large, fill=(255, 255, 255))
        
        # Nível
        levels = xp_db.get_levels(guild_id)
        level_name = 'Sem cargo'
        for lvl in levels:
            if lvl.level == user_data.level:
                level_name = lvl.role_name
                break
        
        draw.text((210, 95), f'Nível {user_data.level} • {level_name}', font=font_small, fill=(150, 150, 150))
        
        # Barra de progresso
        bar_x = 210
        bar_y = 145
        bar_width = 540
        bar_height = 35
        
        # Fundo da barra
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(40, 40, 40))
        
        # Progresso
        next_level_xp = 999999
        current_level_xp = 0
        for lvl in sorted(levels, key=lambda x: x.level):
            if lvl.level == user_data.level + 1:
                next_level_xp = lvl.required_xp
            if lvl.level == user_data.level:
                current_level_xp = lvl.required_xp
        
        xp_in_level = user_data.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress = min(xp_in_level / xp_needed if xp_needed > 0 else 1.0, 1.0)
        
        # Barra preenchida
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            draw.rectangle([bar_x, bar_y, bar_x + filled_width, bar_y + bar_height], fill=(0, 102, 255))
        
        # Texto XP
        xp_text = f'{user_data.xp:,} / {next_level_xp:,} XP'
        bbox = draw.textbbox((0, 0), xp_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        draw.text((bar_x + (bar_width - text_width) // 2, bar_y + 5), xp_text, font=font_small, fill=(255, 255, 255))
        
        # Posição no ranking
        leaderboard = xp_db.get_leaderboard(guild_id, limit=999999)
        rank_position = None
        for idx, lb_user in enumerate(leaderboard, start=1):
            if lb_user.user_id == member.id:
                rank_position = idx
                break
        
        if rank_position:
            rank_text = f'#{rank_position}'
            bbox = draw.textbbox((0, 0), rank_text, font=font_large)
            rank_width = bbox[2] - bbox[0]
            draw.text((CARD_WIDTH - rank_width - 40, 30), rank_text, font=font_large, fill=(0, 102, 255))
        
        # Salvar
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return discord.File(buffer, filename=f'rank_{member.id}.png')
    
    except Exception as e:
        print(f'❌ Erro ao gerar rank card: {e}')
        return None


async def generate_leaderboard_image(bot, guild, top_users):
    """Gera imagem do leaderboard"""
    
    try:
        height = 150 + (len(top_users) * 80)
        img = Image.new('RGB', (800, height), (26, 26, 46))
        draw = ImageDraw.Draw(img)
        
        # Fontes
        try:
            font_title = ImageFont.truetype('arial.ttf', 48)
            font_medium = ImageFont.truetype('arial.ttf', 32)
            font_small = ImageFont.truetype('arial.ttf', 24)
        except:
            font_title = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Título
        draw.text((30, 30), f'🏆 Top {len(top_users)} - {guild.name}', font=font_title, fill=(255, 255, 255))
        
        # Usuários
        y_offset = 120
        for idx, user_data in enumerate(top_users, start=1):
            try:
                member = guild.get_member(user_data.user_id)
                if not member:
                    continue
                
                # Avatar pequeno
                avatar = await download_avatar(member.display_avatar.url)
                if avatar:
                    avatar = make_circular(avatar, 60)
                    img.paste(avatar, (30, y_offset), avatar)
                
                # Posição
                medal = '🥇' if idx == 1 else '🥈' if idx == 2 else '🥉' if idx == 3 else f'#{idx}'
                draw.text((110, y_offset + 5), medal, font=font_medium, fill=(255, 255, 255))
                
                # Nome
                username = member.name if len(member.name) <= 15 else member.name[:12] + '...'
                draw.text((200, y_offset + 5), username, font=font_medium, fill=(255, 255, 255))
                
                # XP
                draw.text((500, y_offset + 5), f'{user_data.xp:,} XP', font=font_medium, fill=(150, 150, 150))
                
                # Nível
                draw.text((650, y_offset + 5), f'Nível {user_data.level}', font=font_small, fill=(150, 150, 150))
                
                y_offset += 80
            except:
                continue
        
        # Salvar
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return discord.File(buffer, filename='leaderboard.png')
    
    except Exception as e:
        print(f'❌ Erro ao gerar leaderboard: {e}')
        return None


print('✅ Image Generator carregado!')
