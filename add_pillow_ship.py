#!/usr/bin/env python3
# Script para adicionar geração de imagem com Pillow (para notebook)

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar imports do Pillow se não existir
if "from PIL import" not in content:
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
import secrets"""

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
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO"""

    content = content.replace(old_imports, new_imports)

# Adicionar função de criar imagem (antes do @bot.command(name='ship'))
ship_image_function = """
# ========================================
# FUNÇÃO PARA GERAR IMAGEM DE SHIP (NOTEBOOK COM PILLOW)
# ========================================

async def create_ship_image_local(user1, user2, ship_value, ship_name):
    \"\"\"Gera imagem de ship usando Pillow (só funciona no notebook)\"\"\"
    try:
        # Tamanho da imagem
        width, height = 800, 400
        
        # Cor de fundo baseada na porcentagem
        if ship_value >= 75:
            bg_color = (40, 15, 25)  # Escuro rosa
        elif ship_value >= 50:
            bg_color = (40, 30, 10)  # Escuro dourado
        else:
            bg_color = (20, 20, 25)  # Escuro cinza
        
        # Criar imagem
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Baixar avatares
        async with aiohttp.ClientSession() as session:
            # Avatar 1
            async with session.get(str(user1.display_avatar.url)) as resp:
                avatar1_data = await resp.read()
                avatar1 = Image.open(BytesIO(avatar1_data)).convert('RGBA').resize((150, 150))
            
            # Avatar 2
            async with session.get(str(user2.display_avatar.url)) as resp:
                avatar2_data = await resp.read()
                avatar2 = Image.open(BytesIO(avatar2_data)).convert('RGBA').resize((150, 150))
        
        # Criar máscaras circulares
        mask = Image.new('L', (150, 150), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 150, 150), fill=255)
        
        # Aplicar máscaras
        avatar1.putalpha(mask)
        avatar2.putalpha(mask)
        
        # Colar avatares
        img.paste(avatar1, (80, 125), avatar1)
        img.paste(avatar2, (570, 125), avatar2)
        
        # Desenhar coração no meio
        heart_x, heart_y = 360, 150
        heart_color = (255, 50, 100) if ship_value >= 50 else (100, 100, 100)
        
        # Coração simplificado
        draw.ellipse([heart_x, heart_y, heart_x+30, heart_y+30], fill=heart_color)
        draw.ellipse([heart_x+20, heart_y, heart_x+50, heart_y+30], fill=heart_color)
        draw.polygon([
            (heart_x+5, heart_y+25),
            (heart_x+45, heart_y+25),
            (heart_x+25, heart_y+55)
        ], fill=heart_color)
        
        # Tentar carregar fonte
        try:
            font_large = ImageFont.truetype("arial.ttf", 40)
            font_medium = ImageFont.truetype("arial.ttf", 30)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Título
        title_text = ship_name.upper()
        draw.text((width//2, 40), title_text, fill=(255, 255, 255), font=font_large, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Porcentagem
        percent_text = f"{ship_value}%"
        draw.text((width//2, 190), percent_text, fill=(255, 200, 0), font=font_large, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Barra de progresso
        bar_x, bar_y = 150, 320
        bar_width, bar_height = 500, 40
        
        # Fundo da barra
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_width, bar_y+bar_height], radius=20, fill=(50, 50, 50))
        
        # Barra preenchida
        filled_width = int(bar_width * (ship_value / 100))
        if filled_width > 0:
            fill_color = (255, 50, 100) if ship_value >= 50 else (100, 100, 100)
            draw.rounded_rectangle([bar_x, bar_y, bar_x+filled_width, bar_y+bar_height], radius=20, fill=fill_color)
        
        # Salvar em BytesIO
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        return output
    
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        import traceback
        traceback.print_exc()
        return None

"""

# Encontrar onde inserir
insert_pos = content.find("@bot.command(name='ship')")
if insert_pos != -1:
    # Verificar se já não existe a função
    if "async def create_ship_image" not in content:
        content = content[:insert_pos] + ship_image_function + content[insert_pos:]

# Atualizar final do comando ship para tentar usar imagem
old_ship_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Enviar embed (sem imagem)
    await ctx.reply(embed=embed)"""

new_ship_end = """    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Tentar gerar imagem (só funciona no notebook com Pillow)
    try:
        ship_image = await create_ship_image_local(user1, user2, ship_value, ship_name)
        
        if ship_image:
            file = discord.File(ship_image, filename='ship.png')
            embed.set_image(url='attachment://ship.png')
            await ctx.reply(embed=embed, file=file)
        else:
            # Se falhar, envia só o embed
            await ctx.reply(embed=embed)
    except Exception as e:
        print(f"⚠️ Pillow não disponível, enviando só embed: {e}")
        await ctx.reply(embed=embed)"""

if old_ship_end in content:
    content = content.replace(old_ship_end, new_ship_end)

# Salvar versão modificada
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Codigo atualizado com geracao de imagem via Pillow!")
print("No notebook, a imagem sera gerada!")
print("No Render, continua sem imagem (Pillow nao compila la)")
