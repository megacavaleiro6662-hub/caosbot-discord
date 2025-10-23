"""
🎨 GERADOR DE RANK CARDS
Cria imagens de XP/nível usando Pillow (PIL)
"""

import discord
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import io
import os
from xp_database import xp_db

# ==================== CONFIGURAÇÕES ====================

CARD_WIDTH = 800
CARD_HEIGHT = 250
AVATAR_SIZE = 150
CORNER_RADIUS = 20

# Fontes (usar fontes padrão se não tiver custom)
try:
    FONT_LARGE = ImageFont.truetype("arial.ttf", 48)
    FONT_MEDIUM = ImageFont.truetype("arial.ttf", 32)
    FONT_SMALL = ImageFont.truetype("arial.ttf", 24)
    FONT_TINY = ImageFont.truetype("arial.ttf", 18)
except:
    # Fallback para fonte padrão
    FONT_LARGE = ImageFont.load_default()
    FONT_MEDIUM = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_TINY = ImageFont.load_default()


# ==================== FUNÇÕES AUXILIARES ====================

async def download_image(url):
    """Baixa imagem de uma URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return Image.open(io.BytesIO(data))
    except Exception as e:
        print(f'❌ Erro ao baixar imagem: {e}')
    return None


def hex_to_rgb(hex_color):
    """Converte cor hex para RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_rounded_rectangle(draw, xy, radius, fill):
    """Desenha retângulo com cantos arredondados"""
    x1, y1, x2, y2 = xy
    
    # Retângulo principal
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    
    # Cantos arredondados
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)


def create_circular_mask(size):
    """Cria máscara circular para avatar"""
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    return mask


# ==================== GERADOR DE RANK CARD ====================

async def generate_rank_card(user, guild_id, config=None):
    """
    Gera rank card completo do usuário
    
    Args:
        user: discord.Member ou discord.User
        guild_id: ID do servidor
        config: XPConfig (se None, busca do banco)
    
    Returns:
        discord.File ou None
    """
    
    try:
        # Pegar config se não foi fornecida
        if not config:
            config = xp_db.get_config(guild_id)
        
        # Pegar dados do usuário
        user_data = xp_db.get_user_xp(guild_id, user.id)
        if not user_data:
            return None
        
        # Pegar nível atual
        levels_config = xp_db.get_levels(guild_id)
        current_level_data = None
        next_level_data = None
        
        for level_data in sorted(levels_config, key=lambda x: x.level):
            if level_data.level == user_data.level:
                current_level_data = level_data
            elif level_data.level == user_data.level + 1:
                next_level_data = level_data
                break
        
        # XP do próximo nível
        if next_level_data:
            next_level_xp = next_level_data.required_xp
        else:
            next_level_xp = user_data.xp  # Já está no nível máximo
        
        # XP do nível atual
        if current_level_data:
            current_level_xp = current_level_data.required_xp
        else:
            current_level_xp = 0
        
        # Progresso no nível atual
        xp_in_level = user_data.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress = min(xp_in_level / xp_needed if xp_needed > 0 else 1.0, 1.0)
        
        # Criar canvas
        if config.image_bg_url:
            # Tentar usar imagem de fundo
            bg_image = await download_image(config.image_bg_url)
            if bg_image:
                bg_image = bg_image.resize((CARD_WIDTH, CARD_HEIGHT))
                img = bg_image
            else:
                img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), hex_to_rgb(config.image_bg_color))
        else:
            # Usar cor sólida
            img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), hex_to_rgb(config.image_bg_color))
        
        # Adicionar overlay semi-transparente
        overlay = Image.new('RGBA', (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 128))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        draw = ImageDraw.Draw(img)
        
        # ==================== AVATAR ====================
        
        avatar_url = user.display_avatar.url
        avatar = await download_image(avatar_url)
        
        if avatar:
            # Redimensionar e tornar circular
            avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))
            mask = create_circular_mask(AVATAR_SIZE)
            
            # Aplicar máscara
            avatar = avatar.convert('RGBA')
            output = Image.new('RGBA', (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
            output.paste(avatar, (0, 0), mask)
            
            # Colar no canvas
            avatar_x = 30
            avatar_y = (CARD_HEIGHT - AVATAR_SIZE) // 2
            img.paste(output, (avatar_x, avatar_y), output)
            
            # Borda do avatar
            draw.ellipse(
                [avatar_x - 3, avatar_y - 3, avatar_x + AVATAR_SIZE + 3, avatar_y + AVATAR_SIZE + 3],
                outline=hex_to_rgb(config.image_bar_color),
                width=4
            )
        
        # ==================== NOME DO USUÁRIO ====================
        
        text_x = 210
        text_color = hex_to_rgb(config.image_text_color)
        
        # Nome
        username = user.name
        if len(username) > 20:
            username = username[:17] + '...'
        
        draw.text((text_x, 40), username, font=FONT_LARGE, fill=text_color)
        
        # ==================== NÍVEL ====================
        
        level_text = f"Nível {user_data.level}"
        if current_level_data:
            level_text += f" • {current_level_data.role_name}"
        
        draw.text((text_x, 95), level_text, font=FONT_SMALL, fill=text_color)
        
        # ==================== BARRA DE PROGRESSO ====================
        
        bar_x = text_x
        bar_y = 145
        bar_width = 540
        bar_height = 35
        
        # Fundo da barra
        create_rounded_rectangle(
            draw,
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            10,
            (40, 40, 40, 200)
        )
        
        # Barra de progresso
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            create_rounded_rectangle(
                draw,
                [bar_x, bar_y, bar_x + filled_width, bar_y + bar_height],
                10,
                hex_to_rgb(config.image_bar_color)
            )
        
        # Texto do XP
        xp_text = f"{user_data.xp:,} / {next_level_xp:,} XP"
        
        # Calcular tamanho do texto
        bbox = draw.textbbox((0, 0), xp_text, font=FONT_TINY)
        text_width = bbox[2] - bbox[0]
        
        # Centralizar na barra
        xp_text_x = bar_x + (bar_width - text_width) // 2
        xp_text_y = bar_y + 7
        
        # Sombra do texto
        draw.text((xp_text_x + 2, xp_text_y + 2), xp_text, font=FONT_TINY, fill=(0, 0, 0, 255))
        draw.text((xp_text_x, xp_text_y), xp_text, font=FONT_TINY, fill=text_color)
        
        # ==================== RANKING ====================
        
        from xp_system import xp_cache
        from xp_database import xp_db
        
        # Buscar posição no ranking
        leaderboard = xp_db.get_leaderboard(guild_id, limit=999999)
        rank_position = None
        for idx, lb_user in enumerate(leaderboard, start=1):
            if lb_user.user_id == user.id:
                rank_position = idx
                break
        
        if rank_position:
            rank_text = f"#{rank_position}"
            
            # Posicionar no canto superior direito
            bbox = draw.textbbox((0, 0), rank_text, font=FONT_LARGE)
            rank_width = bbox[2] - bbox[0]
            rank_x = CARD_WIDTH - rank_width - 40
            rank_y = 30
            
            # Sombra
            draw.text((rank_x + 2, rank_y + 2), rank_text, font=FONT_LARGE, fill=(0, 0, 0, 255))
            draw.text((rank_x, rank_y), rank_text, font=FONT_LARGE, fill=hex_to_rgb(config.image_bar_color))
        
        # ==================== SALVAR E RETORNAR ====================
        
        # Converter para RGB (remover alpha)
        img = img.convert('RGB')
        
        # Salvar em BytesIO
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        # Retornar como discord.File
        return discord.File(buffer, filename=f'rank_{user.id}.png')
    
    except Exception as e:
        print(f'❌ Erro ao gerar rank card: {e}')
        import traceback
        traceback.print_exc()
        return None


# ==================== GERADOR DE LEVEL UP CARD ====================

async def generate_level_up_card(user, level, level_name, xp, config):
    """
    Gera imagem de level up (simplificada)
    
    Args:
        user: discord.Member
        level: Novo nível
        level_name: Nome do nível
        xp: XP total
        config: XPConfig
    
    Returns:
        discord.File ou None
    """
    
    try:
        # Canvas menor para level up
        width = 600
        height = 200
        
        # Cor de fundo
        img = Image.new('RGB', (width, height), hex_to_rgb(config.image_bg_color))
        draw = ImageDraw.Draw(img)
        
        text_color = hex_to_rgb(config.image_text_color)
        accent_color = hex_to_rgb(config.image_bar_color)
        
        # Avatar
        avatar_url = user.display_avatar.url
        avatar = await download_image(avatar_url)
        
        if avatar:
            avatar_size = 120
            avatar = avatar.resize((avatar_size, avatar_size))
            mask = create_circular_mask(avatar_size)
            
            avatar = avatar.convert('RGBA')
            output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0), mask)
            
            avatar_x = 30
            avatar_y = (height - avatar_size) // 2
            
            img = img.convert('RGBA')
            img.paste(output, (avatar_x, avatar_y), output)
            
            # Borda
            draw.ellipse(
                [avatar_x - 3, avatar_y - 3, avatar_x + avatar_size + 3, avatar_y + avatar_size + 3],
                outline=accent_color,
                width=4
            )
        
        # Texto "LEVEL UP!"
        text_x = 180
        draw.text((text_x, 40), "LEVEL UP!", font=FONT_MEDIUM, fill=accent_color)
        
        # Nível
        level_text = f"Nível {level}"
        draw.text((text_x, 85), level_text, font=FONT_LARGE, fill=text_color)
        
        # Nome do cargo
        draw.text((text_x, 140), level_name, font=FONT_SMALL, fill=text_color)
        
        # Salvar
        img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        return discord.File(buffer, filename=f'levelup_{user.id}.png')
    
    except Exception as e:
        print(f'❌ Erro ao gerar level up card: {e}')
        return None


# ==================== GERADOR DE LEADERBOARD ====================

async def generate_leaderboard_image(bot, guild, top_users, config):
    """
    Gera imagem do top 10 ranking
    
    Args:
        bot: Bot instance
        guild: discord.Guild
        top_users: Lista de XPUser
        config: XPConfig
    
    Returns:
        discord.File ou None
    """
    
    try:
        # Canvas maior para leaderboard
        width = 800
        height = 80 + (len(top_users) * 70) + 40  # Header + usuários + padding
        
        # Cor de fundo
        img = Image.new('RGB', (width, height), hex_to_rgb(config.image_bg_color))
        draw = ImageDraw.Draw(img)
        
        text_color = hex_to_rgb(config.image_text_color)
        accent_color = hex_to_rgb(config.image_bar_color)
        
        # Título
        title = f"🏆 TOP {len(top_users)} - {guild.name}"
        draw.text((30, 25), title, font=FONT_LARGE, fill=accent_color)
        
        # Desenhar cada usuário
        y_offset = 100
        
        for idx, user_data in enumerate(top_users, start=1):
            try:
                # Buscar usuário
                user = guild.get_member(user_data.user_id)
                if not user:
                    user = await bot.fetch_user(user_data.user_id)
                
                # Avatar pequeno
                avatar_url = user.display_avatar.url
                avatar = await download_image(avatar_url)
                
                if avatar:
                    avatar_size = 50
                    avatar = avatar.resize((avatar_size, avatar_size))
                    mask = create_circular_mask(avatar_size)
                    
                    avatar = avatar.convert('RGBA')
                    output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
                    output.paste(avatar, (0, 0), mask)
                    
                    img = img.convert('RGBA')
                    img.paste(output, (40, y_offset), output)
                
                # Posição
                pos_text = f"#{idx}"
                draw.text((110, y_offset + 5), pos_text, font=FONT_MEDIUM, fill=accent_color)
                
                # Nome
                username = user.name
                if len(username) > 25:
                    username = username[:22] + '...'
                draw.text((170, y_offset + 5), username, font=FONT_SMALL, fill=text_color)
                
                # XP e Level
                stats_text = f"Level {user_data.level} • {user_data.xp:,} XP"
                draw.text((170, y_offset + 35), stats_text, font=FONT_TINY, fill=text_color)
                
                y_offset += 70
            
            except Exception as e:
                print(f'❌ Erro ao processar usuário {user_data.user_id}: {e}')
                continue
        
        # Salvar
        img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        return discord.File(buffer, filename=f'leaderboard_{guild.id}.png')
    
    except Exception as e:
        print(f'❌ Erro ao gerar leaderboard: {e}')
        import traceback
        traceback.print_exc()
        return None


print('✅ Gerador de imagens carregado!')
