#!/usr/bin/env python3
# Script para usar API externa de ship

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover imports do Pillow
old_imports = """import discord
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
import requests
from datetime import datetime
from discord.ui import Button, View
import math
import threading
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import secrets
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO"""

new_imports = """import discord
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
import requests
from datetime import datetime
from discord.ui import Button, View
import math
import threading
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import secrets
from io import BytesIO"""

content = content.replace(old_imports, new_imports)

# Remover função antiga de criar imagem e adicionar nova usando API
old_ship_function = """# ========================================
# FUNÇÃO PARA GERAR IMAGEM DE SHIP
# ========================================

async def create_ship_image(user1, user2, ship_value, ship_name):
    \"\"\"Cria imagem de ship estilo Loritta\"\"\"
    try:
        # Tamanho da imagem
        width, height = 800, 400
        
        # Criar imagem base com gradiente
        img = Image.new('RGB', (width, height), color='#2C2F33')
        draw = ImageDraw.Draw(img)
        
        # Gradiente de fundo baseado na porcentagem
        if ship_value >= 75:
            color1, color2 = (255, 20, 147), (255, 105, 180)  # Pink
        elif ship_value >= 50:
            color1, color2 = (255, 215, 0), (255, 165, 0)  # Dourado
        elif ship_value >= 25:
            color1, color2 = (135, 206, 235), (70, 130, 180)  # Azul
        else:
            color1, color2 = (128, 128, 128), (64, 64, 64)  # Cinza
        
        # Desenhar gradiente
        for i in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * i / height)
            g = int(color1[1] + (color2[1] - color1[1]) * i / height)
            b = int(color1[2] + (color2[2] - color1[2]) * i / height)
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
        
        # Baixar avatares dos usuários
        async with aiohttp.ClientSession() as session:
            # Avatar 1
            async with session.get(str(user1.display_avatar.url)) as resp:
                avatar1_data = await resp.read()
                avatar1 = Image.open(BytesIO(avatar1_data)).convert('RGBA')
            
            # Avatar 2
            async with session.get(str(user2.display_avatar.url)) as resp:
                avatar2_data = await resp.read()
                avatar2 = Image.open(BytesIO(avatar2_data)).convert('RGBA')
        
        # Redimensionar avatares
        avatar_size = 150
        avatar1 = avatar1.resize((avatar_size, avatar_size), Image.LANCZOS)
        avatar2 = avatar2.resize((avatar_size, avatar_size), Image.LANCZOS)
        
        # Criar máscara circular para os avatares
        mask = Image.new('L', (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        
        # Criar borda branca nos avatares
        border_size = 5
        avatar1_with_border = Image.new('RGBA', (avatar_size + border_size*2, avatar_size + border_size*2), (255, 255, 255, 255))
        avatar2_with_border = Image.new('RGBA', (avatar_size + border_size*2, avatar_size + border_size*2), (255, 255, 255, 255))
        
        # Aplicar máscara circular
        avatar1.putalpha(mask)
        avatar2.putalpha(mask)
        
        # Colar avatares com borda
        avatar1_with_border.paste(avatar1, (border_size, border_size), avatar1)
        avatar2_with_border.paste(avatar2, (border_size, border_size), avatar2)
        
        # Posicionar avatares na imagem
        img.paste(avatar1_with_border, (80, height//2 - (avatar_size + border_size*2)//2), avatar1_with_border)
        img.paste(avatar2_with_border, (width - 80 - avatar_size - border_size*2, height//2 - (avatar_size + border_size*2)//2), avatar2_with_border)
        
        # Adicionar coração no meio
        heart_size = 80
        heart_x = width // 2 - heart_size // 2
        heart_y = height // 2 - heart_size // 2
        
        # Desenhar coração (aproximação com círculos e triângulo)
        heart_color = (255, 0, 0) if ship_value >= 50 else (128, 128, 128)
        draw.ellipse([heart_x, heart_y, heart_x + heart_size//2, heart_y + heart_size//2], fill=heart_color)
        draw.ellipse([heart_x + heart_size//2, heart_y, heart_x + heart_size, heart_y + heart_size//2], fill=heart_color)
        draw.polygon([
            (heart_x, heart_y + heart_size//2),
            (heart_x + heart_size, heart_y + heart_size//2),
            (heart_x + heart_size//2, heart_y + heart_size)
        ], fill=heart_color)
        
        # Tentar carregar fonte (se não tiver, usa padrão)
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Adicionar nome do ship no topo
        ship_text = ship_name.upper()
        bbox = draw.textbbox((0, 0), ship_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 30), ship_text, fill=(255, 255, 255), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Adicionar porcentagem
        percent_text = f"{ship_value}%"
        bbox = draw.textbbox((0, 0), percent_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, height - 80), percent_text, fill=(255, 255, 255), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Adicionar barra de progresso
        bar_width = 600
        bar_height = 30
        bar_x = (width - bar_width) // 2
        bar_y = height - 120
        
        # Fundo da barra
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], radius=15, fill=(50, 50, 50))
        
        # Barra preenchida
        filled_width = int(bar_width * (ship_value / 100))
        if filled_width > 0:
            fill_color = color1 if ship_value >= 50 else (128, 128, 128)
            draw.rounded_rectangle([bar_x, bar_y, bar_x + filled_width, bar_y + bar_height], radius=15, fill=fill_color)
        
        # Salvar em BytesIO
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        return output
    
    except Exception as e:
        print(f"❌ Erro ao criar imagem de ship: {e}")
        return None

"""

new_ship_function = """# ========================================
# FUNÇÃO PARA GERAR IMAGEM DE SHIP COM API EXTERNA
# ========================================

async def create_ship_image(user1, user2, ship_value, ship_name):
    \"\"\"Cria imagem de ship usando API externa some-random-api.com\"\"\"
    try:
        # URL da API com avatares dos usuários
        avatar1_url = str(user1.display_avatar.url)
        avatar2_url = str(user2.display_avatar.url)
        
        # API some-random-api.com para gerar ship
        api_url = f"https://some-random-api.com/canvas/misc/ship?user1={avatar1_url}&user2={avatar2_url}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return BytesIO(image_data)
                else:
                    print(f"❌ Erro na API: Status {resp.status}")
                    return None
    
    except Exception as e:
        print(f"❌ Erro ao gerar imagem de ship: {e}")
        return None

"""

content = content.replace(old_ship_function, new_ship_function)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Ship atualizado para usar API externa!")
