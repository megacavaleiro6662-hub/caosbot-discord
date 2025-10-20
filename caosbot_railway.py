# Bot Discord Caos - Python
# Arquivo principal do bot

import discord
from discord import app_commands
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
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response
from functools import wraps
import secrets
from io import BytesIO
import sqlite3
from urllib.parse import urlencode

# ========================================
# SISTEMA DE MÚSICA REMOVIDO
# ========================================
# Bot focado em moderação, tickets e administração.
# Sistema de música foi removido para maior estabilidade e foco em vendas.

# ========================================
# INICIALIZAR FLASK COM OAUTH2
# ========================================
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Discord OAuth2
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'YOUR_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_OAUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds%20guilds.members.read"

# Log para debug
print(f"🔧 REDIRECT_URI configurado: {DISCORD_REDIRECT_URI}")

# IDs dos cargos PERMITIDOS (apenas Founder, Sub-Dono, Administrador)
ALLOWED_ROLE_IDS = [
    '1365636960651051069',  # Founder
    '1365636456386789437',  # Sub-Dono
    '1365633918593794079'   # Administrador
]

SERVER_ID = '1365510151884378214'  # CAOS Hub

# Função para verificar permissões do usuário
def check_user_permissions(user_id):
    """Verifica se usuário tem cargo de Administrador ou superior EM TEMPO REAL usando BOT TOKEN"""
    try:
        # USA O BOT TOKEN para garantir informações atualizadas
        bot_token = os.getenv('DISCORD_TOKEN')
        if not bot_token:
            return False
        
        headers = {'Authorization': f'Bot {bot_token}'}
        
        # Busca os cargos do usuário no servidor CAOS Hub (SEMPRE ATUALIZADO)
        member_data = requests.get(
            f'https://discord.com/api/guilds/{SERVER_ID}/members/{user_id}',
            headers=headers
        ).json()
        
        print(f"🔐 [CHECK] Usuário {user_id} - Cargos: {member_data.get('roles', [])}")
        
        # Verifica se tem algum dos cargos permitidos
        user_roles = member_data.get('roles', [])
        for role_id in user_roles:
            if role_id in ALLOWED_ROLE_IDS:
                print(f"✅ [CHECK] Usuário {user_id} tem cargo permitido: {role_id}")
                return True
        
        print(f"❌ [CHECK] Usuário {user_id} NÃO tem cargo permitido")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")
        return False

# Decorator para verificar login E permissões em tempo real
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        
        # Verifica permissões em TEMPO REAL
        if not check_user_permissions(session['user']['id']):
            session.clear()
            return """
            <html>
            <head><title>Sessão Expirada</title><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet"></head>
            <body style="background:#000;color:#ff3300;text-align:center;padding-top:100px;font-family:Orbitron,sans-serif;">
                <h1 style="font-size:48px;text-shadow:0 0 20px #ff0000;">⚠️ ACESSO REVOGADO</h1>
                <p style="color:#ff6666;font-size:18px;">Suas permissões de administrador foram removidas.</p>
                <a href="/login" style="color:#ff6600;font-size:16px;text-decoration:none;">← Fazer Login Novamente</a>
            </body>
            </html>
            """
        
        return f(*args, **kwargs)
    return decorated_function

# ========================================
# SERVIDOR HTTP PARA RENDER (DETECTAR PORTA)
# ========================================
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/ping')
def ping():
    """Rota para keep-alive (evitar sleep do Render)"""
    return {"status": "alive", "bot": "online", "uptime": "running"}, 200

@app.route('/test')
def test():
    """Rota de teste para debug"""
    return """
    <html>
        <head><title>TESTE - CAOS Bot</title></head>
        <body style="background: #000; color: #fff; font-family: Arial; padding: 50px; text-align: center;">
            <h1>✅ FLASK ESTÁ FUNCIONANDO!</h1>
            <p>Se você está vendo isso, o servidor Flask está online.</p>
            <hr>
            <h2>Diagnóstico:</h2>
            <p><b>Status:</b> Online</p>
            <p><b>Porta:</b> """ + str(os.getenv("PORT", "10000")) + """</p>
            <p><b>REDIRECT_URI:</b> """ + DISCORD_REDIRECT_URI + """</p>
            <p><b>CLIENT_ID:</b> """ + DISCORD_CLIENT_ID + """</p>
            <hr>
            <a href="/" style="color: #ff6600;">Ir para Home</a> | 
            <a href="/login" style="color: #ff6600;">Ir para Login</a>
        </body>
    </html>
    """, 200
# SISTEMA DE LOGIN COM DISCORD OAUTH2
# ========================================
@app.route('/login')
def login_page():
    """Página de login"""
    # Limpa sessão ao acessar página de login
    session.clear()
    
    html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAOS Hub - Login</title>
    <link rel="icon" href="https://i.ibb.co/Fq5Lgzs5/Chat-GPT-Image-7-de-out-de-2025-00-25-49.png" type="image/png">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Orbitron', sans-serif; }}
        body {{
            background: linear-gradient(135deg, #000000 0%, #1a0000 25%, #330000 50%, #1a0000 75%, #000000 100%);
            background-size: 400% 400%;
            animation: fireGlow 20s ease infinite;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow-y: auto;
        }}
        @keyframes fireGlow {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        .login-container {{
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(50, 0, 0, 0.8) 100%);
            border: 3px solid #ff6600;
            padding: 60px 50px;
            text-align: center;
            box-shadow: 0 16px 64px rgba(255, 50, 0, 0.6), 0 0 40px rgba(255, 100, 0, 0.4);
            max-width: 500px;
            width: 90%;
        }}
        .logo {{
            width: 200px;
            margin-bottom: 30px;
            filter: drop-shadow(0 0 20px rgba(255, 100, 0, 0.8));
        }}
        h1 {{
            font-size: 42px;
            color: #ffcc00;
            margin-bottom: 15px;
            text-shadow: 0 0 15px rgba(255, 200, 0, 0.6);
            letter-spacing: 3px;
        }}
        p {{
            color: #ffaa66;
            font-size: 16px;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }}
        .login-btn {{
            background: linear-gradient(135deg, #ff6600, #ff3300);
            color: white;
            border: 3px solid #ff3300;
            padding: 18px 40px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 2px;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 8px 24px rgba(255, 50, 0, 0.5);
        }}
        .login-btn:hover {{
            background: linear-gradient(135deg, #ff3300, #cc0000);
            box-shadow: 0 12px 32px rgba(255, 50, 0, 0.8);
            transform: translateY(-3px);
        }}
        .warning {{
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 50, 0, 0.1);
            border: 2px solid #ff3300;
            color: #ff6666;
            font-size: 14px;
        }}
        
        /* GIF de fundo tela toda */
        .animated-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            opacity: 0.25;
            filter: hue-rotate(20deg) brightness(1.6) saturate(2.5) drop-shadow(0 0 40px rgba(255, 120, 0, 0.9));
            z-index: 0;
            pointer-events: none;
        }}
        
        .login-container {{
            position: relative;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <!-- GIF animado de fundo -->
    <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDFjZnlmcjdpbjdseTR4ZnU5NWtzOHJhZ3Q0cWp3ZzBrYzFkcWhnbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IeZiGntCfEWOrSjK81/giphy.gif" alt="Animated BG" class="animated-bg">
    
    <div class="login-container">
        <img src="https://i.ibb.co/Fq5Lgzs5/Chat-GPT-Image-7-de-out-de-2025-00-25-49.png" alt="CAOS Logo" class="logo">
        <h1>CAOS HUB</h1>
        <p>Sistema Administrativo Avançado</p>
        <a href="{DISCORD_OAUTH_URL}" class="login-btn">🔐 LOGIN COM DISCORD</a>
        <div class="warning">
            ⚠️ <strong>ACESSO RESTRITO</strong><br>
            Apenas administradores podem acessar este painel.
        </div>
    </div>
</body>
</html>
    """
    return html

@app.route('/callback')
def callback():
    """Callback do Discord OAuth2 - VERIFICAÇÃO PERFEITA DE CARGOS"""
    # Limpa qualquer sessão antiga antes de começar
    session.clear()
    
    code = request.args.get('code')
    if not code:
        return redirect(url_for('login_page'))
    
    try:
        # Trocar código por token
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
        r.raise_for_status()
        token_data = r.json()
        access_token = token_data['access_token']
        
        # Pegar informações do usuário
        headers = {'Authorization': f'Bearer {access_token}'}
        user_data = requests.get('https://discord.com/api/users/@me', headers=headers).json()
        
        print(f"🔐 [LOGIN] Usuário tentando login: {user_data.get('username')} (ID: {user_data.get('id')})")
        
        # VERIFICAÇÃO PERFEITA: Usar Bot Token para pegar cargos do servidor CAOS Hub
        bot_token = os.getenv('DISCORD_TOKEN')
        if not bot_token:
            print("❌ [LOGIN] Bot Token não configurado!")
            raise Exception("Bot Token não configurado")
        
        # Buscar cargos do usuário no servidor CAOS Hub usando BOT TOKEN (sempre atualizado)
        bot_headers = {'Authorization': f'Bot {bot_token}'}
        member_url = f'https://discord.com/api/guilds/{SERVER_ID}/members/{user_data["id"]}'
        
        print(f"🔍 [LOGIN] Verificando membro: {member_url}")
        member_response = requests.get(member_url, headers=bot_headers)
        
        print(f"📡 [LOGIN] Status da API: {member_response.status_code}")
        
        if member_response.status_code == 404:
            print(f"❌ [LOGIN] Usuário não encontrado no servidor")
            print(f"🔍 [LOGIN] Server ID: {SERVER_ID}")
            print(f"🔍 [LOGIN] User ID: {user_data['id']}")
            return """
            <html>
            <head><title>Acesso Negado</title><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet"></head>
            <body style="background:#000;color:#ff3300;text-align:center;padding-top:100px;font-family:Orbitron,sans-serif;">
                <h1 style="font-size:48px;text-shadow:0 0 20px #ff0000;">❌ ACESSO NEGADO</h1>
                <p style="color:#ff6666;font-size:18px;">Você não é membro do servidor CAOS Hub.</p>
                <p style="color:#999;font-size:14px;">Certifique-se de estar no servidor e tenha os cargos necessários.</p>
                <a href="/login" style="color:#ff6600;font-size:16px;text-decoration:none;">← Voltar ao Login</a>
            </body>
            </html>
            """
        
        if member_response.status_code != 200:
            print(f"⚠️ [LOGIN] Erro na API: {member_response.text}")
            return f"""
            <html>
            <head><title>Erro</title></head>
            <body style="background:#000;color:#ff3300;text-align:center;padding-top:100px;font-family:Arial;">
                <h1>❌ Erro ao verificar permissões</h1>
                <p>Status: {member_response.status_code}</p>
                <p>Tente novamente ou contacte um administrador.</p>
                <a href="/login" style="color:#ff6600;">← Voltar</a>
            </body>
            </html>
            """
        
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        print(f"✅ [LOGIN] Cargos carregados: {user_roles}")
        
        print(f"🔐 [LOGIN] Cargos do usuário: {user_roles}")
        print(f"🔐 [LOGIN] Cargos permitidos: {ALLOWED_ROLE_IDS}")
        
        # Verificar se tem algum cargo permitido (Founder, Sub-Dono ou Administrador)
        has_permission = False
        role_encontrado = None
        
        for role_id in user_roles:
            if role_id in ALLOWED_ROLE_IDS:
                has_permission = True
                # Descobrir qual cargo
                if role_id == '1365636960651051069':
                    role_encontrado = 'Founder'
                elif role_id == '1365636456386789437':
                    role_encontrado = 'Sub-Dono'
                elif role_id == '1365633918593794079':
                    role_encontrado = 'Administrador'
                break
        
        if not has_permission:
            print(f"❌ [LOGIN] Usuário NÃO tem cargo permitido (Founder/Sub-Dono/Administrador)")
            return """
            <html>
            <head><title>Acesso Negado</title><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet"></head>
            <body style="background:#000;color:#ff3300;text-align:center;padding-top:100px;font-family:Orbitron,sans-serif;">
                <h1 style="font-size:48px;text-shadow:0 0 20px #ff0000;">❌ ACESSO NEGADO</h1>
                <p style="color:#ff6666;font-size:18px;">Você precisa ter cargo de <strong>Founder</strong>, <strong>Sub-Dono</strong> ou <strong>Administrador</strong>.</p>
                <a href="/login" style="color:#ff6600;font-size:16px;text-decoration:none;">← Voltar ao Login</a>
            </body>
            </html>
            """
        
        print(f"✅ [LOGIN] Usuário autorizado com cargo: {role_encontrado}")
        
        # Salvar na sessão (com access_token para verificação contínua)
        session['access_token'] = access_token
        session['user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'avatar': f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data.get('avatar') else None
        }
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        print(f"❌ [LOGIN] Erro: {e}")
        return f"<html><body style='background:#000;color:#ff3300;text-align:center;padding:50px;font-family:Orbitron;'><h1>❌ Erro no login</h1><p>{str(e)}</p><a href='/login' style='color:#ff6600;'>← Voltar</a></body></html>", 500

@app.route('/logout')
def logout():
    """Fazer logout"""
    session.clear()
    return redirect(url_for('login_page'))

# CARREGAMENTO DE CONFIGURAÇÕES
@app.route('/health')
def health():
    return {"status": "online", "bot": "CAOSBot", "lavalink": "active"}
    """Endpoint para testar conexão dashboard → bot"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        message = data.get('message', '🧪 TESTE DE CONEXÃO DASHBOARD → BOT')
        
        print(f"🧪 [TEST] Recebida requisição de teste para canal {channel_id}")
        
        # Agendar envio de mensagem
        async def send_test():
            try:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    await channel.send(f"✅ {message}\n⏰ Horário: {datetime.now().strftime('%H:%M:%S')}")
                    print(f"✅ [TEST] Mensagem enviada para {channel.name}")
                    return True
                else:
                    print(f"❌ [TEST] Canal {channel_id} não encontrado")
                    return False
            except Exception as e:
                print(f"❌ [TEST] Erro ao enviar: {e}")
                return False
        
        # Executar de forma assíncrona
        future = asyncio.run_coroutine_threadsafe(send_test(), bot.loop)
        result = future.result(timeout=10)
        
        if result:
            return jsonify({"success": True, "message": "Mensagem enviada com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Canal não encontrado"}), 404
            
    except Exception as e:
        print(f"❌ [TEST] Erro crítico: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ========================================
# ROTAS DO DASHBOARD WEB
# ========================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Página principal do dashboard"""
    try:
        config = load_config_dashboard()
        
        # HTML embutido (não precisa de templates/)
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAOS Hub - Dashboard</title>
    <link rel="icon" href="https://i.ibb.co/Fq5Lgzs5/Chat-GPT-Image-7-de-out-de-2025-00-25-49.png" type="image/png">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Orbitron', 'Rajdhani', sans-serif; }}
        
        /* Animação de fogo no fundo */
        @keyframes fireGlow {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        @keyframes fireFloat {{
            0% {{ transform: translateY(100vh) scale(0); opacity: 0; }}
            10% {{ opacity: 1; }}
            90% {{ opacity: 1; }}
            100% {{ transform: translateY(-100vh) scale(1.5); opacity: 0; }}
        }}
        
        @keyframes fireFlicker {{
            0%, 100% {{ opacity: 0.6; }}
            50% {{ opacity: 1; }}
        }}
        
        body {{ 
            font-family: 'Inter', 'Roboto', sans-serif; 
            background: linear-gradient(135deg, #000000 0%, #1a0000 25%, #330000 50%, #1a0000 75%, #000000 100%);
            background-size: 400% 400%;
            animation: fireGlow 20s ease infinite;
            min-height: 100vh; 
            color: #fff; 
            overflow-y: auto;
            position: relative;
        }}
        
        /* Partículas de fogo animadas */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 10% 90%, rgba(255, 50, 0, 0.15) 0%, transparent 30%),
                radial-gradient(circle at 90% 10%, rgba(255, 100, 0, 0.12) 0%, transparent 35%),
                radial-gradient(circle at 50% 50%, rgba(255, 150, 0, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 30% 20%, rgba(255, 200, 0, 0.06) 0%, transparent 25%);
            animation: fireFlicker 3s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }}
        
        body::after {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle 150px at 15% 80%, rgba(255, 100, 0, 0.2) 0%, transparent 100%),
                radial-gradient(circle 200px at 85% 20%, rgba(255, 150, 0, 0.15) 0%, transparent 100%),
                radial-gradient(circle 100px at 50% 60%, rgba(255, 200, 0, 0.1) 0%, transparent 100%);
            animation: fireFloat 25s linear infinite;
            pointer-events: none;
            z-index: 0;
        }}
        
        /* Camada extra de partículas */
        .fire-particles {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow-y: auto;
            pointer-events: none;
            z-index: 0;
        }}
        
        .particle {{
            position: absolute;
            bottom: -50px;
            width: 5px;
            height: 5px;
            background: radial-gradient(circle, #ffcc00, #ff6600, transparent);
            border-radius: 50%;
            opacity: 0;
            animation: rise 15s linear infinite;
            box-shadow: 0 0 10px #ff6600, 0 0 20px #ff3300;
        }}
        
        /* Partículas vermelhas */
        .particle:nth-child(3n) {{
            background: radial-gradient(circle, #ff3300, #cc0000, transparent);
            box-shadow: 0 0 10px #ff3300, 0 0 20px #ff0000;
        }}
        
        /* Partículas amarelas */
        .particle:nth-child(5n) {{
            background: radial-gradient(circle, #ffff00, #ffcc00, transparent);
            box-shadow: 0 0 15px #ffcc00, 0 0 25px #ffaa00;
        }}
        
        /* Estrelas (forma diferente) */
        .particle:nth-child(7n) {{
            width: 8px;
            height: 8px;
            background: linear-gradient(45deg, transparent 40%, #fff 40%, #fff 60%, transparent 60%),
                        linear-gradient(-45deg, transparent 40%, #fff 40%, #fff 60%, transparent 60%);
            border-radius: 0;
            box-shadow: 0 0 15px #fff, 0 0 30px #ffcc00;
        }}
        
        /* Partículas maiores */
        .particle:nth-child(11n) {{
            width: 8px;
            height: 8px;
        }}
        
        @keyframes rise {{
            0% {{ transform: translateY(0) translateX(0) scale(0.5); opacity: 0; }}
            10% {{ opacity: 0.8; }}
            50% {{ opacity: 1; }}
            90% {{ opacity: 0.5; }}
            100% {{ transform: translateY(-100vh) translateX(var(--drift)) scale(1.5); opacity: 0; }}
        }}
        
        .particle:nth-child(1) {{ left: 10%; animation-delay: 0s; animation-duration: 12s; --drift: 30px; }}
        .particle:nth-child(2) {{ left: 20%; animation-delay: 2s; animation-duration: 15s; --drift: -20px; }}
        .particle:nth-child(3) {{ left: 30%; animation-delay: 4s; animation-duration: 13s; --drift: 40px; }}
        .particle:nth-child(4) {{ left: 40%; animation-delay: 1s; animation-duration: 14s; --drift: -30px; }}
        .particle:nth-child(5) {{ left: 50%; animation-delay: 3s; animation-duration: 16s; --drift: 25px; }}
        .particle:nth-child(6) {{ left: 60%; animation-delay: 5s; animation-duration: 12s; --drift: -40px; }}
        .particle:nth-child(7) {{ left: 70%; animation-delay: 2.5s; animation-duration: 15s; --drift: 35px; }}
        .particle:nth-child(8) {{ left: 80%; animation-delay: 4.5s; animation-duration: 13s; --drift: -25px; }}
        .particle:nth-child(9) {{ left: 90%; animation-delay: 1.5s; animation-duration: 14s; --drift: 20px; }}
        .particle:nth-child(10) {{ left: 15%; animation-delay: 6s; animation-duration: 17s; --drift: -35px; }}
        .particle:nth-child(11) {{ left: 25%; animation-delay: 3.5s; animation-duration: 11s; --drift: 45px; }}
        .particle:nth-child(12) {{ left: 35%; animation-delay: 5.5s; animation-duration: 16s; --drift: -15px; }}
        .particle:nth-child(13) {{ left: 45%; animation-delay: 0.5s; animation-duration: 13s; --drift: 30px; }}
        .particle:nth-child(14) {{ left: 55%; animation-delay: 4.2s; animation-duration: 15s; --drift: -40px; }}
        .particle:nth-child(15) {{ left: 65%; animation-delay: 2.8s; animation-duration: 12s; --drift: 50px; }}
        .particle:nth-child(16) {{ left: 75%; animation-delay: 6.5s; animation-duration: 14s; --drift: -20px; }}
        .particle:nth-child(17) {{ left: 85%; animation-delay: 1.2s; animation-duration: 16s; --drift: 35px; }}
        .particle:nth-child(18) {{ left: 95%; animation-delay: 3.8s; animation-duration: 13s; --drift: -45px; }}
        .particle:nth-child(19) {{ left: 5%; animation-delay: 5.2s; animation-duration: 15s; --drift: 25px; }}
        .particle:nth-child(20) {{ left: 12%; animation-delay: 0.8s; animation-duration: 17s; --drift: -30px; }}
        .particle:nth-child(21) {{ left: 18%; animation-delay: 7s; animation-duration: 14s; --drift: 35px; }}
        .particle:nth-child(22) {{ left: 28%; animation-delay: 1.8s; animation-duration: 16s; --drift: -25px; }}
        .particle:nth-child(23) {{ left: 38%; animation-delay: 4.8s; animation-duration: 12s; --drift: 40px; }}
        .particle:nth-child(24) {{ left: 48%; animation-delay: 2.2s; animation-duration: 15s; --drift: -35px; }}
        .particle:nth-child(25) {{ left: 58%; animation-delay: 6.2s; animation-duration: 13s; --drift: 30px; }}
        .particle:nth-child(26) {{ left: 68%; animation-delay: 3.2s; animation-duration: 17s; --drift: -40px; }}
        .particle:nth-child(27) {{ left: 78%; animation-delay: 5.8s; animation-duration: 11s; --drift: 45px; }}
        .particle:nth-child(28) {{ left: 88%; animation-delay: 0.3s; animation-duration: 14s; --drift: -20px; }}
        .particle:nth-child(29) {{ left: 8%; animation-delay: 4.3s; animation-duration: 16s; --drift: 35px; }}
        .particle:nth-child(30) {{ left: 22%; animation-delay: 7.3s; animation-duration: 13s; --drift: -30px; }}
        .particle:nth-child(31) {{ left: 32%; animation-delay: 2.7s; animation-duration: 15s; --drift: 40px; }}
        .particle:nth-child(32) {{ left: 42%; animation-delay: 5.3s; animation-duration: 12s; --drift: -25px; }}
        .particle:nth-child(33) {{ left: 52%; animation-delay: 1.3s; animation-duration: 17s; --drift: 30px; }}
        .particle:nth-child(34) {{ left: 62%; animation-delay: 6.7s; animation-duration: 14s; --drift: -35px; }}
        .particle:nth-child(35) {{ left: 72%; animation-delay: 3.7s; animation-duration: 11s; --drift: 45px; }}
        .particle:nth-child(36) {{ left: 82%; animation-delay: 0.7s; animation-duration: 16s; --drift: -40px; }}
        .particle:nth-child(37) {{ left: 92%; animation-delay: 4.7s; animation-duration: 13s; --drift: 35px; }}
        .particle:nth-child(38) {{ left: 6%; animation-delay: 2.3s; animation-duration: 15s; --drift: -30px; }}
        .particle:nth-child(39) {{ left: 16%; animation-delay: 5.7s; animation-duration: 12s; --drift: 40px; }}
        .particle:nth-child(40) {{ left: 26%; animation-delay: 1.7s; animation-duration: 17s; --drift: -25px; }}
        .particle:nth-child(41) {{ left: 36%; animation-delay: 6.3s; animation-duration: 14s; --drift: 35px; }}
        .particle:nth-child(42) {{ left: 46%; animation-delay: 3.3s; animation-duration: 11s; --drift: -40px; }}
        .particle:nth-child(43) {{ left: 56%; animation-delay: 7.7s; animation-duration: 16s; --drift: 45px; }}
        .particle:nth-child(44) {{ left: 66%; animation-delay: 0.4s; animation-duration: 13s; --drift: -35px; }}
        .particle:nth-child(45) {{ left: 76%; animation-delay: 4.4s; animation-duration: 15s; --drift: 30px; }}
        .particle:nth-child(46) {{ left: 86%; animation-delay: 2.4s; animation-duration: 12s; --drift: -25px; }}
        .particle:nth-child(47) {{ left: 96%; animation-delay: 5.4s; animation-duration: 17s; --drift: 40px; }}
        .particle:nth-child(48) {{ left: 11%; animation-delay: 1.4s; animation-duration: 14s; --drift: -30px; }}
        .particle:nth-child(49) {{ left: 21%; animation-delay: 6.4s; animation-duration: 11s; --drift: 35px; }}
        .particle:nth-child(50) {{ left: 31%; animation-delay: 3.4s; animation-duration: 16s; --drift: -45px; }}
        .sidebar {{ 
            position: fixed; 
            left: 0; 
            top: 0; 
            width: 280px; 
            height: 100vh; 
            background: linear-gradient(180deg, #000000 0%, #1a0000 100%); 
            backdrop-filter: blur(10px); 
            border-right: 3px solid #ff3300; 
            padding: 32px 24px; 
            z-index: 10; 
            box-shadow: 5px 0 30px rgba(255, 50, 0, 0.3);
            overflow-y: auto;
        }}
        
        @keyframes hueShift {{
            0% {{ filter: blur(2px) hue-rotate(0deg); }}
            50% {{ filter: blur(2px) hue-rotate(30deg); }}
            100% {{ filter: blur(2px) hue-rotate(0deg); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(1.2); }}
        }}
        
        .sidebar::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZm9oNzBoaDFrbzh5OTZiMXZ0eTF0Zms0bWE5Z3pveXQ5NGJuNWY4eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/L6VKg3ruTIfFFiKWpw/giphy.gif') center/cover;
            opacity: 0.2;
            z-index: -1;
            pointer-events: none;
            animation: hueShift 8s ease-in-out infinite;
        }}
        
        .sidebar-logo {{ display: flex; align-items: center; justify-content: center; margin-bottom: 40px; position: relative; z-index: 1; }}
        .sidebar-logo img {{ width: 180px; height: auto; filter: drop-shadow(0 0 20px rgba(255, 100, 0, 0.8)); }}
        .sidebar-nav {{ list-style: none; }}
        .sidebar-nav li {{ margin-bottom: 12px; }}
        .sidebar-nav a {{ display: flex; align-items: center; padding: 14px 18px; color: #ffaa66; text-decoration: none; border-radius: 0; border-left: 4px solid transparent; transition: all 0.3s; font-weight: 600; letter-spacing: 0.5px; }}
        .sidebar-nav a:hover {{ background: rgba(255, 100, 0, 0.15); color: #ffcc00; border-left-color: #ff6600; box-shadow: inset 0 0 10px rgba(255, 100, 0, 0.2); }}
        .sidebar-nav a.active {{ background: rgba(255, 50, 0, 0.25); color: #ffffff; border-left-color: #ff3300; box-shadow: inset 0 0 15px rgba(255, 50, 0, 0.3); }}
        .main {{ margin-left: 280px; padding: 32px; position: relative; z-index: 1; }}
        .header {{ background: linear-gradient(135deg, rgba(255, 50, 0, 0.15) 0%, rgba(255, 100, 0, 0.1) 100%); backdrop-filter: blur(10px); border: 2px solid #ff6600; border-radius: 0; padding: 32px; margin-bottom: 32px; box-shadow: 0 8px 32px rgba(255, 50, 0, 0.4); display: flex; justify-content: space-between; align-items: center; }}
        .header-left h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; text-shadow: 0 0 10px rgba(255, 100, 0, 0.5), 0 0 20px rgba(255, 50, 0, 0.3); color: #ffcc00; }}
        .header-left p {{ color: #ffaa66; font-size: 16px; }}
        .user-profile {{ display: flex; align-items: center; gap: 16px; }}
        .user-avatar {{ width: 48px; height: 48px; border-radius: 50%; border: 2px solid #ff6600; box-shadow: 0 0 10px rgba(255, 100, 0, 0.5); }}
        .user-info {{ text-align: right; }}
        .user-name {{ font-size: 16px; font-weight: 700; color: #ffcc00; text-shadow: 0 0 5px rgba(255, 200, 0, 0.4); }}
        .user-role {{ font-size: 13px; color: #ffaa66; margin-top: 4px; }}
        .btn-logout {{ padding: 8px 16px; background: linear-gradient(135deg, #cc0000, #990000); color: white; border: 2px solid #cc0000; border-radius: 0; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 12px rgba(200, 0, 0, 0.4); }}
        .btn-logout:hover {{ background: linear-gradient(135deg, #990000, #660000); box-shadow: 0 6px 16px rgba(200, 0, 0, 0.6); transform: translateY(-2px); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }}
        .card {{ background: linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(50, 0, 0, 0.4) 100%); backdrop-filter: blur(10px); border: 2px solid #ff6600; border-radius: 0; padding: 24px; transition: all 0.3s; box-shadow: 0 4px 16px rgba(255, 50, 0, 0.3); }}
        .card:hover {{ border-color: #ff3300; transform: translateY(-4px); box-shadow: 0 8px 24px rgba(255, 100, 0, 0.5), 0 0 30px rgba(255, 50, 0, 0.3); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .card-header h2 {{ font-size: 18px; font-weight: 700; color: #ffcc00; text-shadow: 0 0 5px rgba(255, 200, 0, 0.4); }}
        .toggle {{ position: relative; width: 48px; height: 24px; }}
        .toggle input {{ opacity: 0; width: 0; height: 0; }}
        .toggle label {{ position: absolute; cursor: pointer; inset: 0; background: #330000; transition: 0.3s; border-radius: 0; border: 1px solid #ff6600; }}
        .toggle label:before {{ content: ""; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px; background: linear-gradient(135deg, #ff6600, #ffcc00); transition: 0.3s; border-radius: 0; box-shadow: 0 0 5px rgba(255, 200, 0, 0.5); }}
        .toggle input:checked + label {{ background: linear-gradient(135deg, #ff3300, #ff6600); box-shadow: 0 0 10px rgba(255, 50, 0, 0.6); }}
        .toggle input:checked + label:before {{ transform: translateX(24px); background: linear-gradient(135deg, #ffcc00, #ffffff); }}
        .status {{ display: inline-block; padding: 4px 12px; border-radius: 0; font-size: 12px; font-weight: 600; border: 1px solid; }}
        .status-on {{ background: rgba(255, 200, 0, 0.15); color: #ffcc00; border-color: #ffaa00; text-shadow: 0 0 5px rgba(255, 200, 0, 0.4); }}
        .status-off {{ background: rgba(100, 0, 0, 0.3); color: #ff6666; border-color: #ff3300; }}
        .btn {{ padding: 12px 24px; border: 2px solid; border-radius: 0; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s; letter-spacing: 0.5px; }}
        .btn-primary {{ background: linear-gradient(135deg, #ff6600, #ff3300); color: white; border-color: #ff3300; box-shadow: 0 4px 15px rgba(255, 50, 0, 0.4); }}
        .btn-primary:hover {{ background: linear-gradient(135deg, #ff3300, #cc0000); box-shadow: 0 6px 20px rgba(255, 50, 0, 0.6), 0 0 20px rgba(255, 100, 0, 0.4); transform: translateY(-2px); }}
        .btn-danger {{ background: linear-gradient(135deg, #cc0000, #990000); color: white; border-color: #cc0000; box-shadow: 0 4px 15px rgba(200, 0, 0, 0.4); }}
        .btn-danger:hover {{ background: linear-gradient(135deg, #990000, #660000); box-shadow: 0 6px 20px rgba(200, 0, 0, 0.6); transform: translateY(-2px); }}
        .section {{ margin-bottom: 32px; }}
        .section-title {{ font-size: 20px; font-weight: 700; margin-bottom: 16px; color: #ffcc00; text-shadow: 0 0 8px rgba(255, 200, 0, 0.4); }}
        .page {{ display: none; }}
        .page.active {{ display: block; }}
        .form-group {{ margin-bottom: 16px; }}
        .form-label {{ display: block; margin-bottom: 8px; font-size: 14px; font-weight: 600; color: #ffaa66; }}
        .form-input, .form-select, .form-textarea {{ width: 100%; padding: 10px 14px; background: rgba(0, 0, 0, 0.5); border: 2px solid #ff6600; border-radius: 0; color: #ffcc00; font-family: 'Inter', 'Roboto', sans-serif; font-size: 14px; transition: all 0.3s; }}
        .form-input:focus, .form-select:focus, .form-textarea:focus {{ outline: none; border-color: #ff3300; box-shadow: 0 0 10px rgba(255, 50, 0, 0.4), inset 0 0 5px rgba(255, 100, 0, 0.2); background: rgba(20, 0, 0, 0.6); }}
        .form-textarea {{ resize: vertical; min-height: 100px; }}
        .toast {{ position: fixed; top: 24px; right: 24px; background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(50, 0, 0, 0.9)); border: 2px solid #ff6600; border-radius: 0; padding: 16px; min-width: 300px; opacity: 0; transform: translateX(400px); transition: all 0.3s; z-index: 1000; box-shadow: 0 8px 32px rgba(255, 50, 0, 0.5), 0 0 20px rgba(255, 100, 0, 0.3); }}
        .toast.show {{ opacity: 1; transform: translateX(0); }}
        .toast-success {{ border-color: #ffcc00; box-shadow: 0 8px 32px rgba(255, 200, 0, 0.5), 0 0 20px rgba(255, 200, 0, 0.3); }}
        .toast-error {{ border-color: #ff3300; box-shadow: 0 8px 32px rgba(255, 50, 0, 0.6), 0 0 20px rgba(255, 0, 0, 0.4); }}
    </style>
</head>
<body>
    <!-- Partículas de fogo animadas (50 partículas variadas) -->
    <div class="fire-particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo">
            <img src="https://i.ibb.co/Fq5Lgzs5/Chat-GPT-Image-7-de-out-de-2025-00-25-49.png" alt="CAOS Hub">
        </div>
        <ul class="sidebar-nav">
            <li><a href="#" class="active" onclick="showPage('dashboard')">📊 Dashboard</a></li>
            <li><a href="#" onclick="showPage('tickets')">🎫 Tickets</a></li>
            <li><a href="#" onclick="showPage('embeds')">📋 Embeds</a></li>
            <li><a href="#" onclick="showPage('stats')">📈 Estatísticas</a></li>
        </ul>
    </div>
    
    <!-- Main Content -->
    <div class="main">
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <h1>Painel de Controle</h1>
                <p>Gerencie seu bot Discord de forma profissional</p>
            </div>
            <div class="user-profile">
                <div class="user-info">
                    <div class="user-name" id="user-display-name">Carregando...</div>
                    <div class="user-role" id="user-display-role">•••</div>
                </div>
                <img src="" alt="Avatar" class="user-avatar" id="user-avatar">
                <button class="btn-logout" onclick="window.location.href='/logout'">🚪 Sair</button>
            </div>
        </div>
        
        <!-- Dashboard Page -->
        <div id="dashboard-page" class="page active">
            <div class="section">
                <h2 class="section-title">Configurações do Servidor</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <h2>👋 Boas-vindas</h2>
                            <div class="toggle">
                                <input type="checkbox" id="welcome_enabled" {"checked" if config.get('welcome_enabled') else ""}>
                                <label for="welcome_enabled"></label>
                            </div>
                        </div>
                        <span id="welcome-status" class="status {'status-on' if config.get('welcome_enabled') else 'status-off'}">
                            {'Ativado' if config.get('welcome_enabled') else 'Desativado'}
                        </span>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <h2>👋 Saída/Ban</h2>
                            <div class="toggle">
                                <input type="checkbox" id="goodbye_enabled" {"checked" if config.get('goodbye_enabled') else ""}>
                                <label for="goodbye_enabled"></label>
                            </div>
                        </div>
                        <span id="goodbye-status" class="status {'status-on' if config.get('goodbye_enabled') else 'status-off'}">
                            {'Ativado' if config.get('goodbye_enabled') else 'Desativado'}
                        </span>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <h2>🎭 Autorole</h2>
                            <div class="toggle">
                                <input type="checkbox" id="autorole_enabled" {"checked" if config.get('autorole_enabled') else ""}>
                                <label for="autorole_enabled"></label>
                            </div>
                        </div>
                        <span id="autorole-status" class="status {'status-on' if config.get('autorole_enabled') else 'status-off'}">
                            {'Ativado' if config.get('autorole_enabled') else 'Desativado'}
                        </span>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <h2>🎫 Tickets</h2>
                            <div class="toggle">
                                <input type="checkbox" id="tickets_enabled" {"checked" if config.get('tickets_enabled') else ""}>
                                <label for="tickets_enabled"></label>
                            </div>
                        </div>
                        <span id="tickets-status" class="status {'status-on' if config.get('tickets_enabled') else 'status-off'}">
                            {'Ativado' if config.get('tickets_enabled') else 'Desativado'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tickets Page -->
        <div id="tickets-page" class="page">
            <div class="section">
                <h2 class="section-title">🎫 Configuração Completa de Tickets</h2>
                
                <!-- Sub-tabs -->
                <div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
                    <button class="btn btn-primary" style="padding: 8px 16px; font-size: 13px;" onclick="showTicketTab('basico')">⚙️ Básico</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('painel')">🎨 Painel</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('categorias')">📋 Categorias</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('prioridades')">⚡ Prioridades</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('mensagens')">💬 Mensagens</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('campos')">📝 Campos</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('avancado')">🔧 Avançado</button>
                    <button class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);" onclick="showTicketTab('logs')">📊 Logs</button>
                </div>
                
                <!-- Aba Básico -->
                <div id="ticket-tab-basico" class="ticket-tab">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">⚙️ Configuração Básica + Enviar Painel</h3>
                        
                        <div class="form-group">
                            <label class="form-label">📁 1. Categoria Destino (onde criar tickets)</label>
                            <select id="ticket-category" class="form-select" onchange="loadChannelsByCategory()">
                                <option value="">Carregando categorias...</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📣 2. Canal para Enviar Painel</label>
                            <select id="ticket-channel" class="form-select" disabled>
                                <option value="">Selecione uma categoria primeiro</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📢 3. Canal de Logs (ticket-logs)</label>
                            <select id="ticket-log-channel" class="form-select">
                                <option value="">Carregando canais...</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">👥 4. Cargos da Staff (quem vê tickets)</label>
                            <div id="ticket-staff-roles" style="display: grid; gap: 8px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; max-height: 200px; overflow-y: auto;">
                                <div style="color: #9ca3af;">Carregando cargos...</div>
                            </div>
                            <small style="color: #9ca3af; margin-top: 5px; display: block;">✅ Selecione os cargos que poderão ver os tickets</small>
                        </div>
                        
                        <hr style="border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
                        
                        <div class="form-group">
                            <label class="form-label">✏️ Título do Painel</label>
                            <input type="text" id="ticket-title" class="form-input" value="🎫 SISTEMA DE TICKETS">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📝 Descrição</label>
                            <textarea id="ticket-description" class="form-textarea">Clique no botão abaixo para abrir um ticket e falar com a equipe!</textarea>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🎨 Cor do Embed</label>
                            <input type="color" id="ticket-color-picker" value="#5865F2" style="width: 60px; height: 40px;">
                        </div>
                        
                        <button class="btn btn-primary" onclick="sendTicketPanel(event)" style="width: 100%; padding: 15px; font-size: 16px; margin-top: 10px;">🚀 Enviar Painel Agora</button>
                    </div>
                </div>
                
                <!-- Aba Painel -->
                <div id="ticket-tab-painel" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">🎨 Personalização Avançada</h3>
                        <p style="color: #9ca3af;">Configurações básicas de envio estão na aba "Básico"</p>
                        <p style="color: #9ca3af;">Esta aba está reservada para customizações futuras.</p>
                    </div>
                </div>
                
                <!-- Aba Categorias -->
                <div id="ticket-tab-categorias" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">📋 Categorias Disponíveis</h3>
                        <p style="color: #9ca3af; margin-bottom: 15px;">Ative/desative categorias (aparecem no dropdown)</p>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 📁 Geral
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🛒 Compras
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🔧 Suporte Técnico
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🚨 Denúncia
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🤝 Parceria
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🎉 Sorteios
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 💰 Financeiro
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🛡️ Moderação
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer;">
                                <input type="checkbox" checked> 🐛 Bug
                            </label>
                        </div>
                    </div>
                </div>
                
                <!-- Aba Prioridades -->
                <div id="ticket-tab-prioridades" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">⚡ Sistema de Prioridades</h3>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px;">
                            <input type="checkbox" checked> Ativar sistema de prioridades
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px;">
                            <input type="checkbox" checked> Usar cores baseadas na prioridade
                        </label>
                        <div style="display: grid; gap: 10px; margin-top: 20px;">
                            <div style="padding: 10px; background: rgba(0,255,0,0.1); border-radius: 8px;">🟢 Baixa - Não é urgente</div>
                            <div style="padding: 10px; background: rgba(255,255,0,0.1); border-radius: 8px;">🟡 Média - Prioridade normal</div>
                            <div style="padding: 10px; background: rgba(255,136,0,0.1); border-radius: 8px;">🟠 Alta - Precisa de atenção</div>
                            <div style="padding: 10px; background: rgba(255,0,0,0.1); border-radius: 8px;">🔴 Urgente - Muito urgente!</div>
                        </div>
                    </div>
                </div>
                
                <!-- Aba Mensagens -->
                <div id="ticket-tab-mensagens" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">💬 Mensagens Customizáveis</h3>
                        <div class="form-group">
                            <label class="form-label">👋 Mensagem de Boas-vindas</label>
                            <textarea class="form-textarea">Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.</textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">📝 Mensagem no Embed</label>
                            <textarea class="form-textarea">Nossa equipe responderá o mais breve possível!</textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">🔒 Mensagem ao Fechar</label>
                            <input type="text" class="form-input" value="🔒 Fechando ticket em 3 segundos...">
                        </div>
                    </div>
                </div>
                
                <!-- Aba Campos -->
                <div id="ticket-tab-campos" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">📝 Campos do Modal</h3>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked disabled> 📄 Assunto (obrigatório)
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked disabled> 📝 Descrição (obrigatório)
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 🌐 Idioma
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> ℹ️ Informações Adicionais
                        </label>
                    </div>
                </div>
                
                <!-- Aba Avançado -->
                <div id="ticket-tab-avancado" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">🔧 Configurações Avançadas</h3>
                        <div class="form-group">
                            <label class="form-label">🔢 Limite de tickets por usuário</label>
                            <input type="number" class="form-input" value="1" min="1" max="10">
                        </div>
                        <div class="form-group">
                            <label class="form-label">⏰ Cooldown (minutos)</label>
                            <input type="number" class="form-input" value="0" min="0" max="60">
                        </div>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 📊 Ativar transcrições
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 📈 Ativar estatísticas
                        </label>
                    </div>
                </div>
                
                <!-- Aba Logs -->
                <div id="ticket-tab-logs" class="ticket-tab" style="display:none;">
                    <div class="card">
                        <h3 style="margin-bottom: 20px;">📊 Configuração de Logs</h3>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 📢 Ativar sistema de logs
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 📊 Incluir estatísticas
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 📁 Anexar transcrição (.txt)
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> 👥 Mostrar participantes
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                            <input type="checkbox" checked> ⏱️ Mostrar duração
                        </label>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <button class="btn btn-primary" style="width: 100%; padding: 15px;">💾 Salvar Todas as Configurações</button>
                </div>
            </div>
        </div>
        
        <!-- Embeds Page -->
        <div id="embeds-page" class="page">
            <div class="section">
                <h2 class="section-title">📋 Gerador de Embeds Visual</h2>
                
                <!-- Seletor de Template -->
                <div class="card" style="margin-bottom: 24px;">
                    <div class="card-header">
                        <h2>🎨 Escolha um Template</h2>
                    </div>
                    <div class="form-group">
                        <select id="embed-template" class="form-select" onchange="loadEmbedTemplate()">
                            <option value="custom">✏️ Personalizado</option>
                            <option value="giveaway">🎉 Giveaway</option>
                            <option value="rules">📜 Regras</option>
                            <option value="announcement">📢 Anúncio</option>
                            <option value="info">📝 Informações</option>
                            <option value="warning">⚠️ Avisos</option>
                            <option value="success">✅ Confirmação</option>
                        </select>
                    </div>
                </div>
                
                <!-- Grid Editor + Preview -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                    
                    <!-- Editor -->
                    <div class="card">
                        <div class="card-header">
                            <h2>✏️ Editor</h2>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📝 Título do Embed</label>
                            <input type="text" id="embed-title" class="form-input" placeholder="Digite o título" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📄 Descrição</label>
                            <textarea id="embed-description" class="form-textarea" rows="4" placeholder="Digite a descrição (suporta markdown)" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()"></textarea>
                        </div>
                        
                        <!-- Campos específicos do Giveaway -->
                        <div id="giveaway-fields" style="display: none;">
                            <div class="form-group">
                                <label class="form-label">🎁 Prêmio</label>
                                <input type="text" id="giveaway-prize" class="form-input" placeholder="Ex: Nitro Classic, R$50 Steam" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">⏰ Duração do Sorteio</label>
                                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                                    <input type="number" id="giveaway-duration" class="form-input" placeholder="Ex: 7" min="1" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">
                                    <select id="giveaway-time-unit" class="form-select" onchange="updateEmbedPreview()">
                                        <option value="m">Minutos</option>
                                        <option value="h">Horas</option>
                                        <option value="d" selected>Dias</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">👥 Número de Vencedores</label>
                                <input type="number" id="giveaway-winners" class="form-input" placeholder="1" value="1" min="1" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">🎉 Emoji de Reação</label>
                                <input type="text" id="giveaway-emoji" class="form-input" placeholder="🎉" value="🎉" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">🏆 Mensagem do Vencedor</label>
                                <textarea id="giveaway-winner-message" class="form-textarea" rows="3" placeholder="Ex: Parabéns! Você ganhou {{{{prize}}}}! Abra um ticket para receber seu prêmio." oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()">🎊 **Parabéns!** 🎊

Você ganhou **{{{{prize}}}}**!

📋 Abra um ticket na categoria 🎉 **Sorteios** para receber seu prêmio.</textarea>
                                <small style="color: #ffaa66; font-size: 12px;">Use {{{{prize}}}} para o nome do prêmio | {{{{winners}}}} para mencionar vencedores</small>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🎨 Cor do Embed</label>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <input type="color" id="embed-color-picker" value="#ff6600" onchange="updateEmbedColor()" style="width: 60px; height: 40px; cursor: pointer; border: 2px solid #ff6600; background: transparent;">
                                <input type="text" id="embed-color" class="form-input" value="0xff6600" style="flex: 1;" readonly>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🖼️ URL da Imagem (opcional)</label>
                            <input type="text" id="embed-image" class="form-input" placeholder="https://exemplo.com/imagem.png" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🖼️ URL do Thumbnail (opcional)</label>
                            <input type="text" id="embed-thumbnail" class="form-input" placeholder="https://exemplo.com/thumb.png" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">👤 Autor (opcional)</label>
                            <input type="text" id="embed-author" class="form-input" placeholder="Nome do autor" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🔗 URL do Autor (opcional)</label>
                            <input type="text" id="embed-author-url" class="form-input" placeholder="https://exemplo.com" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <!-- Campos customizáveis -->
                        <div style="margin-top: 24px; padding-top: 24px; border-top: 2px solid #ff6600;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                <label class="form-label" style="margin: 0;">📋 Campos (Fields)</label>
                                <button type="button" class="btn btn-primary" onclick="addEmbedField(); return false;" style="padding: 8px 16px; font-size: 13px;">+ Adicionar Campo</button>
                            </div>
                            <div id="embed-fields-container"></div>
                        </div>
                        
                        <div style="margin-top: 24px; padding-top: 24px; border-top: 2px solid #ff6600;">
                            <label class="form-label">📌 Footer (opcional)</label>
                            <input type="text" id="embed-footer" class="form-input" placeholder="Texto do footer" onkeyup="updateEmbedPreview()" style="margin-bottom: 10px;">
                            <input type="text" id="embed-footer-icon" class="form-input" placeholder="URL do ícone do footer" onkeyup="updateEmbedPreview()">
                        </div>
                        
                        <div class="form-group" style="margin-top: 24px;">
                            <label class="form-label">🕒 Timestamp</label>
                            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                                <input type="checkbox" id="embed-timestamp" onchange="updateEmbedPreview()">
                                <span style="color: #ffaa66;">Adicionar timestamp atual</span>
                            </label>
                        </div>
                        
                        <div class="form-group" style="margin-top: 24px;">
                            <label class="form-label">💬 Mensagem Fora do Embed (opcional)</label>
                            <textarea id="embed-extra-message" class="form-textarea" rows="2" placeholder="Ex: @everyone Novo sorteio!" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()"></textarea>
                            <small style="color: #ffaa66; font-size: 12px;">Esta mensagem aparece ACIMA do embed (use para mencionar @everyone)</small>
                        </div>
                    </div>
                    
                    <!-- Preview -->
                    <div style="position: sticky; top: 20px;">
                        <div class="card">
                            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                                <h2>👁️ Preview</h2>
                                <select id="preview-mode" class="form-select" onchange="updateEmbedPreview()" style="width: auto; padding: 8px; font-size: 13px;">
                                    <option value="giveaway">🎉 Sorteio</option>
                                    <option value="winner">🏆 Vencedor</option>
                                </select>
                            </div>
                            <div id="embed-preview" style="background: #2b2d31; padding: 16px; border-radius: 4px; min-height: 300px; max-height: 600px; overflow-y: auto;">
                                <div style="color: #b9bbbe; text-align: center; padding: 40px 20px;">
                                    📝 Configure o embed ao lado para ver o preview aqui
                                </div>
                            </div>
                        </div>
                        
                        <!-- Enviar -->
                        <div class="card" style="margin-top: 24px;">
                            <div class="form-group">
                                <label class="form-label">📁 Categoria</label>
                                <select id="embed-category" class="form-select" onchange="loadEmbedChannelsByCategory()">
                                    <option value="">Carregando categorias...</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">📍 Canal de Destino</label>
                                <select id="embed-channel" class="form-select">
                                    <option value="">Selecione uma categoria primeiro...</option>
                                </select>
                            </div>
                            <button class="btn btn-primary" onclick="sendEmbed()" style="width: 100%; padding: 15px; font-size: 16px;">
                                📤 Enviar Embed
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Stats Page -->
        <div id="stats-page" class="page">
            <div class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <h2 class="section-title" style="margin: 0;">📈 Estatísticas do Servidor</h2>
                    <span style="color: #22c55e; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; animation: pulse 2s infinite;"></span>
                        🔴 LIVE - Tempo Real
                    </span>
                </div>
                <div class="grid" id="stats-grid">
                    <div class="card"><h3>⏳ Carregando...</h3></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Notification -->
    <div id="toast" class="toast"></div>
    
    <!-- Notification Sound (som épico mais longo) -->
    <audio id="notif-sound" preload="auto">
        <source src="https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c6c7c579.mp3" type="audio/mpeg">
    <script>
        // Navegação entre páginas
        function showPage(page) {{
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
            document.getElementById(page + '-page').classList.add('active');
            event.target.classList.add('active');
            
            if (page === 'tickets') {{
                loadCategories();
                // Fechar conexão SSE se estava ativa
                if (statsEventSource) {{
                    statsEventSource.close();
                    statsEventSource = null;
                }}
            }} else if (page === 'stats') {{
                loadStats(); // Inicia conexão em tempo real
            }} else {{
                // Fechar conexão SSE se mudou de página
                if (statsEventSource) {{
                    statsEventSource.close();
                    statsEventSource = null;
                }}
            }}
        }}
        
        // Navegação entre abas de tickets
        function showTicketTab(tab) {{
            // Esconder todas as abas
            document.querySelectorAll('.ticket-tab').forEach(t => t.style.display = 'none');
            
            // Remover active de todos os botões
            const buttons = document.querySelectorAll('#tickets-page .btn');
            buttons.forEach(b => b.style.background = 'rgba(255,255,255,0.1)');
            
            // Mostrar aba selecionada
            document.getElementById('ticket-tab-' + tab).style.display = 'block';
            
            // Marcar botão como ativo
            event.target.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }}
        
        // Notificação com som
        function showToast(message, type = 'success') {{
            const toast = document.getElementById('toast');
            const sound = document.getElementById('notif-sound');
            toast.textContent = message;
            toast.className = `toast toast-${{type}} show`;
            sound.play().catch(() => {{}});
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}
        
        // Toggle de configurações
        document.querySelectorAll('.toggle input').forEach(toggle => {{
            toggle.addEventListener('change', async function() {{
                const key = this.id;
                const statusSpan = document.getElementById(key.replace('_enabled', '-status'));
                try {{
                    const response = await fetch('/api/config/toggle', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ key }})
                    }});
                    const data = await response.json();
                    if (data.success) {{
                        statusSpan.textContent = data.new_value ? 'Ativado' : 'Desativado';
                        statusSpan.className = `status ${{data.new_value ? 'status-on' : 'status-off'}}`;
                        showToast(data.message);
                    }} else {{
                        this.checked = !this.checked;
                        showToast(data.message || 'Erro ao atualizar', 'error');
                    }}
                }} catch (error) {{
                    this.checked = !this.checked;
                    showToast('Erro de conexão', 'error');
                }}
            }});
        }});
        
        // Carregar categorias do Discord
        async function loadCategories() {{
            try {{
                const response = await fetch('/api/discord/categories');
                const data = await response.json();
                const select = document.getElementById('ticket-category');
                select.innerHTML = '<option value="">Selecione uma categoria...</option>';
                if (data.success) {{
                    data.categories.forEach(cat => {{
                        const opt = document.createElement('option');
                        opt.value = cat.id;
                        opt.textContent = cat.name;
                        select.appendChild(opt);
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar categorias:', error);
            }}
            
            // Carregar todos os canais de texto para logs
            loadAllTextChannels();
        }}
        
        // Carregar canais de uma categoria específica
        async function loadChannelsByCategory() {{
            const categoryId = document.getElementById('ticket-category').value;
            const channelSelect = document.getElementById('ticket-channel');
            
            if (!categoryId) {{
                channelSelect.disabled = true;
                channelSelect.innerHTML = '<option value="">Selecione uma categoria primeiro</option>';
                return;
            }}
            
            try {{
                const response = await fetch(`/api/discord/channels/${{categoryId}}`);
                const data = await response.json();
                
                channelSelect.innerHTML = '<option value="">Selecione um canal...</option>';
                channelSelect.disabled = false;
                
                if (data.success && data.channels) {{
                    data.channels.forEach(ch => {{
                        const opt = document.createElement('option');
                        opt.value = ch.id;
                        opt.textContent = ch.name;
                        channelSelect.appendChild(opt);
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar canais:', error);
                channelSelect.innerHTML = '<option value="">Erro ao carregar</option>';
            }}
        }}
        
        // Carregar todos os canais de texto (para logs)
        async function loadAllTextChannels() {{
            try {{
                const response = await fetch('/api/discord/text-channels');
                const data = await response.json();
                const select = document.getElementById('ticket-log-channel');
                
                select.innerHTML = '<option value="">Selecione um canal...</option>';
                
                if (data.success && data.channels) {{
                    data.channels.forEach(ch => {{
                        const opt = document.createElement('option');
                        opt.value = ch.id;
                        opt.textContent = ch.name;
                        select.appendChild(opt);
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar canais de texto:', error);
            }}
            
            // Carregar roles (cargos) também
            loadStaffRoles();
        }}
        
        // Carregar cargos do servidor (para staff)
        async function loadStaffRoles() {{
            try {{
                const response = await fetch('/api/discord/roles');
                const data = await response.json();
                const container = document.getElementById('ticket-staff-roles');
                
                container.innerHTML = '';
                
                if (data.success && data.roles) {{
                    data.roles.forEach(role => {{
                        const label = document.createElement('label');
                        label.style.cssText = 'display: flex; align-items: center; gap: 8px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; cursor: pointer; transition: all 0.2s;';
                        label.onmouseover = () => label.style.background = 'rgba(255,255,255,0.1)';
                        label.onmouseout = () => label.style.background = 'rgba(255,255,255,0.05)';
                        
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.value = role.id;
                        checkbox.className = 'staff-role-checkbox';
                        checkbox.checked = true; // Todos selecionados por padrão
                        
                        const text = document.createElement('span');
                        text.textContent = role.name;
                        
                        label.appendChild(checkbox);
                        label.appendChild(text);
                        container.appendChild(label);
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar cargos:', error);
            }}
        }}
        
        // EventSource para atualização em tempo real
        let statsEventSource = null;
        
        // Renderizar estatísticas no grid
        function renderStats(data) {{
            const grid = document.getElementById('stats-grid');
            if (data.success) {{
                grid.innerHTML = `
                    <div class="card">
                        <h3>👥 Membros Totais</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px;">${{data.total_members}}</p>
                        <p style="font-size: 14px; color: #999; margin-top: 8px;">👤 ${{data.total_humans}} humanos • 🤖 ${{data.total_bots}} bots</p>
                    </div>
                    <div class="card">
                        <h3>🟢 Humanos Online</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px; color: #22c55e;">${{data.humans_online}}</p>
                        <p style="font-size: 14px; color: #999; margin-top: 8px;">de ${{data.total_humans}} humanos</p>
                    </div>
                    <div class="card">
                        <h3>🤖 Robôs Online</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px; color: #3b82f6;">${{data.bots_online}}</p>
                        <p style="font-size: 14px; color: #999; margin-top: 8px;">de ${{data.total_bots}} bots</p>
                    </div>
                    <div class="card">
                        <h3>💬 Canais de Texto</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px;">${{data.text_channels}}</p>
                    </div>
                    <div class="card">
                        <h3>🎙️ Canais de Voz</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px;">${{data.voice_channels}}</p>
                    </div>
                    <div class="card">
                        <h3>🎭 Cargos Totais</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px;">${{data.total_roles}}</p>
                    </div>
                    <div class="card">
                        <h3>🚀 Boost Level</h3>
                        <p style="font-size: 32px; font-weight: 800; margin-top: 16px; color: #f472b6;">${{data.boost_level}}</p>
                    </div>
                `;
            }} else {{
                grid.innerHTML = '<div class="card"><h3>❌ Erro ao carregar estatísticas</h3></div>';
            }}
        }}
        
        // Carregar estatísticas em tempo real com SSE
        function loadStats() {{
            const grid = document.getElementById('stats-grid');
            
            // Fechar conexão anterior se existir
            if (statsEventSource) {{
                statsEventSource.close();
            }}
            
            // Criar nova conexão SSE
            statsEventSource = new EventSource('/api/server/stats/stream');
            
            statsEventSource.onmessage = function(event) {{
                try {{
                    const data = JSON.parse(event.data);
                    renderStats(data);
                }} catch (error) {{
                    console.error('Erro ao processar stats:', error);
                }}
            }};
            
            statsEventSource.onerror = function(error) {{
                console.error('Erro no SSE:', error);
                grid.innerHTML = '<div class="card"><h3>❌ Erro de conexão em tempo real</h3></div>';
                // Reconectar após 3 segundos
                setTimeout(() => {{
                    if (document.getElementById('stats-page').classList.contains('active')) {{
                        loadStats();
                    }}
                }}, 3000);
            }};
        }}
        
        // Color picker
        const colorPicker = document.getElementById('ticket-color-picker');
        const colorInput = document.getElementById('ticket-color');
        
        if (colorPicker && colorInput) {{
            colorPicker.addEventListener('input', function() {{
                const hex = this.value.replace('#', '');
                colorInput.value = '0x' + hex;
            }});
        }}
        
        // Enviar painel de ticket
        async function sendTicketPanel(e) {{
            e.preventDefault();
            const btn = e.target;
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = '⏳ Enviando...';
            
            // Validar campos
            const channelId = document.getElementById('ticket-channel').value;
            const categoryId = document.getElementById('ticket-category').value;
            const logChannelId = document.getElementById('ticket-log-channel').value;
            const title = document.getElementById('ticket-title').value;
            const description = document.getElementById('ticket-description').value;
            
            // Coletar CHECKBOXES marcados (cargos de staff)
            const staffCheckboxes = document.querySelectorAll('.staff-role-checkbox:checked');
            const staffRoles = Array.from(staffCheckboxes).map(cb => cb.value);
            
            if (!channelId) {{
                showToast('❌ Selecione um canal para enviar o painel!', 'error');
                btn.disabled = false;
                btn.textContent = originalText;
                return;
            }}
            
            if (staffRoles.length === 0) {{
                showToast('❌ Selecione pelo menos 1 cargo de staff!', 'error');
                btn.disabled = false;
                btn.textContent = originalText;
                return;
            }}
            
            try {{
                // Converter cor para hex
                const colorPicker = document.getElementById('ticket-color-picker');
                const hexColor = colorPicker.value.replace('#', '');
                
                const response = await fetch('/api/tickets/panel/send', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        channel_id: channelId,
                        category_id: categoryId,
                        log_channel_id: logChannelId,
                        staff_roles: staffRoles,  // Array de IDs
                        title: title,
                        description: description,
                        color: '0x' + hexColor
                    }})
                }});
                
                const data = await response.json();
                if (data.success) {{
                    showToast('🎉 Painel enviado e configurações salvas com sucesso!');
                }} else {{
                    showToast(data.message || 'Erro ao enviar painel', 'error');
                }}
            }} catch (error) {{
                console.error('Erro:', error);
                showToast('❌ Erro de conexão', 'error');
            }} finally {{
                btn.disabled = false;
                btn.textContent = originalText;
            }}
        }}
        // ========================================
        // VERIFICAÇÃO DE PERMISSÕES EM TEMPO REAL (POLLING A CADA 1 SEGUNDO)
        // ========================================
        let authCheckInterval;
        
        function startAuthCheck() {{
            authCheckInterval = setInterval(async () => {{
                try {{
                    const response = await fetch('/api/auth/check');
                    const data = await response.json();
                    
                    if (!data.authorized) {{
                        clearInterval(authCheckInterval);
                        
                        // Mostra tela de acesso revogado
                        document.body.innerHTML = `
                            <div style="
                                position: fixed;
                                top: 0;
                                left: 0;
                                width: 100%;
                                height: 100%;
                                background: #000;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                z-index: 999999;
                            ">
                                <div style="
                                    text-align: center;
                                    font-family: 'Orbitron', sans-serif;
                                    animation: fadeIn 0.5s ease-in;
                                ">
                                    <h1 style="
                                        font-size: 64px;
                                        color: #ff3300;
                                        margin-bottom: 20px;
                                        text-shadow: 0 0 30px #ff0000;
                                    ">⚠️ ACESSO REVOGADO</h1>
                                    <p style="
                                        font-size: 24px;
                                        color: #ff6666;
                                        margin-bottom: 40px;
                                    ">Suas permissões de administrador foram removidas.</p>
                                    <a href="/login" style="
                                        background: linear-gradient(135deg, #ff6600, #ff3300);
                                        color: white;
                                        border: 3px solid #ff3300;
                                        padding: 18px 40px;
                                        font-size: 18px;
                                        font-weight: 700;
                                        text-decoration: none;
                                        display: inline-block;
                                        box-shadow: 0 8px 24px rgba(255, 50, 0, 0.5);
                                        transition: all 0.3s;
                                    ">← Voltar ao Login</a>
                                </div>
                            </div>
                            <style>
                                @keyframes fadeIn {{
                                    from {{ opacity: 0; transform: scale(0.9); }}
                                    to {{ opacity: 1; transform: scale(1); }}
                                }}
                            </style>
                        `;
                    }}
                }} catch (error) {{
                    console.error('Erro ao verificar autenticação:', error);
                }}
            }}, 1000); // Verifica A CADA 1 SEGUNDO
        }}
        
        // Inicia verificação quando página carregar
        startAuthCheck();
        
        // Para a verificação quando sair da página
        window.addEventListener('beforeunload', () => {{
            clearInterval(authCheckInterval);
        }});
        
        // Carregar perfil do usuário no header
        async function loadUserProfile() {{
            try {{
                const response = await fetch('/api/user/profile');
                const data = await response.json();
                
                if (data.success) {{
                    document.getElementById('user-display-name').textContent = data.username;
                    document.getElementById('user-display-role').textContent = data.role || 'Administrador';
                    if (data.avatar) {{
                        document.getElementById('user-avatar').src = data.avatar;
                    }} else {{
                        document.getElementById('user-avatar').src = 'https://cdn.discordapp.com/embed/avatars/0.png';
                    }}
                }} else {{
                    document.getElementById('user-display-name').textContent = 'Usuário';
                    document.getElementById('user-display-role').textContent = 'Admin';
                    document.getElementById('user-avatar').src = 'https://cdn.discordapp.com/embed/avatars/0.png';
                }}
            }} catch (error) {{
                console.error('Erro ao carregar perfil:', error);
            }}
        }}
        
        // ========================================
        // SISTEMA DE EMBEDS
        // ========================================
        
        let embedFieldCount = 0;
        
        // Carregar templates de embeds
        function loadEmbedTemplate() {{
            const template = document.getElementById('embed-template').value;
            
            // Limpar campos existentes SEMPRE que trocar template
            const container = document.getElementById('embed-fields-container');
            if (container) {{
                container.innerHTML = '';
            }}
            embedFieldCount = 0;
            
            // Mostrar/esconder campos específicos
            const giveawayFields = document.getElementById('giveaway-fields');
            if (template === 'giveaway') {{
                giveawayFields.style.display = 'block';
            }} else {{
                giveawayFields.style.display = 'none';
            }}
            
            const templates = {{
                giveaway: {{
                    title: '🎉 GIVEAWAY',
                    description: '', // Será gerado dinamicamente
                    color: '#e91e63',
                    footer: 'Hospedado por CAOS Hub',
                    timestamp: true
                }},
                rules: {{
                    title: '📜 REGRAS DO SERVIDOR',
                    description: '**Leia e siga todas as regras:**\\n\\n1️⃣ Respeite todos os membros\\n2️⃣ Sem spam ou flood\\n3️⃣ Sem conteúdo NSFW\\n4️⃣ Sem divulgação sem permissão\\n5️⃣ Use os canais corretos\\n\\n**Punições:** Warn → Mute → Ban',
                    color: '#f44336',
                    footer: 'Staff do CAOS Hub'
                }},
                announcement: {{
                    title: '📢 ANÚNCIO IMPORTANTE',
                    description: '**Novidades no servidor!**\\n\\nFique atento às atualizações e novidades que estão por vir!\\n\\n@everyone',
                    color: '#ff9800',
                    author: 'CAOS Hub',
                    timestamp: true
                }},
                info: {{
                    title: '📝 INFORMAÇÕES',
                    description: 'Informações importantes sobre o servidor.',
                    color: '#2196f3',
                    footer: 'CAOS Hub - Sistema de Informações'
                }},
                warning: {{
                    title: '⚠️ ATENÇÃO',
                    description: '**Aviso importante para todos os membros!**\\n\\nPor favor, leiam com atenção.',
                    color: '#ffc107',
                    timestamp: true
                }},
                success: {{
                    title: '✅ SUCESSO',
                    description: 'Operação realizada com sucesso!',
                    color: '#4caf50',
                    footer: 'Sistema CAOS Bot'
                }}
            }};
            
            if (template !== 'custom' && templates[template]) {{
                const data = templates[template];
                document.getElementById('embed-title').value = data.title || '';
                document.getElementById('embed-description').value = data.description || '';
                document.getElementById('embed-author').value = data.author || '';
                document.getElementById('embed-footer').value = data.footer || '';
                document.getElementById('embed-timestamp').checked = data.timestamp || false;
                
                // Converter cor
                if (data.color) {{
                    const hex = data.color;
                    document.getElementById('embed-color-picker').value = hex;
                    document.getElementById('embed-color').value = '0x' + hex.replace('#', '');
                }}
                
                updateEmbedPreview();
            }}
        }}
        
        // Atualizar cor do embed
        function updateEmbedColor() {{
            const picker = document.getElementById('embed-color-picker');
            const hex = picker.value.replace('#', '');
            document.getElementById('embed-color').value = '0x' + hex;
            updateEmbedPreview();
        }}
        
        // Adicionar campo ao embed
        function addEmbedField() {{
            embedFieldCount++;
            const container = document.getElementById('embed-fields-container');
            const fieldHTML = `
                <div class="embed-field" id="field-${{embedFieldCount}}" style="border: 2px solid #ff6600; padding: 12px; margin-bottom: 12px; border-radius: 4px; background: rgba(255, 100, 0, 0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="color: #ffcc00; font-weight: 600;">Campo ${{embedFieldCount}}</span>
                        <button type="button" onclick="removeEmbedField(${{embedFieldCount}}); return false;" style="background: #cc0000; color: white; border: none; padding: 4px 8px; cursor: pointer; border-radius: 2px; font-size: 12px;">❌ Remover</button>
                    </div>
                    <input type="text" class="form-input field-name" placeholder="Nome do campo" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()" style="margin-bottom: 8px;">
                    <textarea class="form-textarea field-value" rows="2" placeholder="Valor do campo" oninput="updateEmbedPreview()" onkeyup="updateEmbedPreview()"></textarea>
                    <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; cursor: pointer;">
                        <input type="checkbox" class="field-inline" onchange="updateEmbedPreview()">
                        <span style="color: #ffaa66; font-size: 13px;">Inline (lado a lado)</span>
                    </label>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', fieldHTML);
            updateEmbedPreview();
        }}
        
        // Remover campo
        function removeEmbedField(id) {{
            const el = document.getElementById('field-' + id);
            if (el) {{
                el.remove();
                updateEmbedPreview();
            }}
        }}
        
        // Atualizar preview do embed
        function updateEmbedPreview() {{
            const template = document.getElementById('embed-template').value;
            const previewMode = document.getElementById('preview-mode') ? document.getElementById('preview-mode').value : 'giveaway';
            
            // Se for modo vencedor E template giveaway, mostrar preview do vencedor
            if (template === 'giveaway' && previewMode === 'winner') {{
                showWinnerPreview();
                return;
            }}
            
            const title = document.getElementById('embed-title').value;
            let description = document.getElementById('embed-description').value;
            
            // Gerar descrição dinamicamente para giveaway
            if (template === 'giveaway') {{
                const prize = document.getElementById('giveaway-prize').value || 'Não especificado';
                const duration = document.getElementById('giveaway-duration').value || '7';
                const unit = document.getElementById('giveaway-time-unit').value;
                const winners = document.getElementById('giveaway-winners').value || '1';
                const emoji = document.getElementById('giveaway-emoji').value || '🎉';
                
                let timeText = '';
                if (unit === 'm') timeText = duration + ' minuto' + (duration > 1 ? 's' : '');
                else if (unit === 'h') timeText = duration + ' hora' + (duration > 1 ? 's' : '');
                else timeText = duration + ' dia' + (duration > 1 ? 's' : '');
                
                description = `**Reaja com ${{emoji}} para participar!**\n\n🎁 **Prêmio:** ${{prize}}\n⏰ **Duração:** ${{timeText}}\n👥 **Vencedores:** ${{winners}}\n\n**Boa sorte a todos!** 🍀`;
                
                // Atualizar o textarea (opcional, para mostrar a descrição gerada)
                document.getElementById('embed-description').value = description;
            }}
            const colorPicker = document.getElementById('embed-color-picker').value;
            const image = document.getElementById('embed-image').value;
            const thumbnail = document.getElementById('embed-thumbnail').value;
            const author = document.getElementById('embed-author').value;
            const footer = document.getElementById('embed-footer').value;
            const footerIcon = document.getElementById('embed-footer-icon').value;
            const timestamp = document.getElementById('embed-timestamp').checked;
            
            // Coletar fields
            const fields = [];
            document.querySelectorAll('.embed-field').forEach(field => {{
                const nameEl = field.querySelector('.field-name');
                const valueEl = field.querySelector('.field-value');
                const inlineEl = field.querySelector('.field-inline');
                
                if (nameEl && valueEl) {{
                    const name = nameEl.value;
                    const value = valueEl.value;
                    const inline = inlineEl ? inlineEl.checked : false;
                    
                    if (name || value) {{
                        fields.push({{ name: name || 'Campo', value: value || 'Valor', inline }});
                    }}
                }}
            }});
            
            // Mensagem extra
            const extraMessage = document.getElementById('embed-extra-message').value;
            
            // Gerar preview HTML (estilo Discord REAL)
            let previewHTML = `
            <style>
                .discord-message {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
                    background: #313338;
                    padding: 16px;
                    border-radius: 4px;
                }}
                .discord-message * {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
                }}
                .message-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                }}
                .bot-avatar {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin-right: 12px;
                }}
                .bot-name {{
                    font-size: 15px;
                    font-weight: 500;
                    color: #f2f3f5;
                    margin-right: 6px;
                }}
                .bot-tag {{
                    background: #5865f2;
                    color: #fff;
                    font-size: 10px;
                    font-weight: 500;
                    padding: 2px 4px;
                    border-radius: 3px;
                    text-transform: uppercase;
                    vertical-align: middle;
                }}
                .embed-container {{
                    display: flex;
                    margin-left: 52px;
                }}
                .embed-content {{
                    border-left: 4px solid ` + colorPicker + `;
                    background: #2b2d31;
                    padding: 8px 12px 12px 12px;
                    border-radius: 4px;
                    max-width: 520px;
                    flex: 1;
                    position: relative;
                }}
                .embed-author {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    font-size: 13px;
                    color: #f2f3f5;
                    font-weight: 600;
                }}
                .embed-title {{
                    color: #00aff4;
                    font-size: 15px;
                    font-weight: 600;
                    margin-bottom: 8px;
                    line-height: 1.2;
                }}
                .embed-description {{
                    color: #dbdee1;
                    font-size: 14px;
                    line-height: 1.375;
                    margin-bottom: 8px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .embed-fields {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 8px;
                    margin-top: 8px;
                }}
                .embed-field {{
                    min-width: 0;
                }}
                .embed-field-name {{
                    color: #f2f3f5;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 2px;
                }}
                .embed-field-value {{
                    color: #dbdee1;
                    font-size: 14px;
                    line-height: 1.375;
                }}
                .embed-image {{
                    max-width: 100%;
                    border-radius: 4px;
                    margin-top: 16px;
                }}
                .embed-thumbnail {{
                    position: absolute;
                    right: 12px;
                    top: 8px;
                    width: 80px;
                    height: 80px;
                    object-fit: cover;
                    border-radius: 4px;
                }}
                .embed-footer {{
                    display: flex;
                    align-items: center;
                    margin-top: 8px;
                    padding-top: 8px;
                    border-top: 1px solid #404249;
                    font-size: 12px;
                    color: #b5bac1;
                    font-weight: 500;
                }}
                .embed-footer-icon {{
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
            </style>
            
            <div class="discord-message">
                <div class="message-header">
                    <img src="https://i.ibb.co/VpPdrYCk/Chat-GPT-Image-11-de-set-de-2025-18-35-32.png" class="bot-avatar">
                    <span class="bot-name">CAOS Bot</span>
                    <span class="bot-tag">BOT</span>
                </div>
                <div style="margin-left: 52px;">
            `;
            
            // Adicionar mensagem extra se tiver (como texto normal do Discord)
            if (extraMessage) {{
                previewHTML += `<div style="color: #dcddde; font-size: 16px; margin-bottom: 8px; line-height: 1.375; word-wrap: break-word;">${{extraMessage}}</div>`;
            }}
            
            previewHTML += `
                <div class="embed-container">
                    <div class="embed-content">
            `;
            
            // Thumbnail
            if (thumbnail) {{
                previewHTML += '<img src="' + thumbnail + '" class="embed-thumbnail" onerror="this.style.display=\\'none\\'">';
            }}
            
            // Author
            if (author) {{
                previewHTML += '<div class="embed-author">' + author + '</div>';
            }}
            
            // Title
            if (title) {{
                previewHTML += '<div class="embed-title">' + title + '</div>';
            }}
            
            // Description
            if (description) {{
                let desc = description.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                desc = desc.replace(/\*(.*?)\*/g, '<em>$1</em>');
                desc = desc.replace(/\\n/g, '<br>');  // Quebrar linhas
                previewHTML += '<div class="embed-description">' + desc + '</div>';
            }}
            
            // Fields
            if (fields.length > 0) {{
                previewHTML += '<div class="embed-fields">';
                fields.forEach(f => {{
                    previewHTML += '<div class="embed-field" style="' + (f.inline ? '' : 'grid-column: 1 / -1;') + '">';
                    previewHTML += '<div class="embed-field-name">' + (f.name || 'Campo') + '</div>';
                    previewHTML += '<div class="embed-field-value">' + (f.value || 'Valor') + '</div>';
                    previewHTML += '</div>';
                }});
                previewHTML += '</div>';
            }}
            
            // Image
            if (image) {{
                previewHTML += '<img src="' + image + '" class="embed-image" onerror="this.style.display=\\'none\\'">';
            }}
            
            // Footer
            if (footer || timestamp) {{
                previewHTML += '<div class="embed-footer">';
                if (footerIcon) {{
                    previewHTML += '<img src="' + footerIcon + '" class="embed-footer-icon" onerror="this.style.display=\\'none\\'">';
                }}
                if (footer) {{
                    previewHTML += '<span>' + footer + '</span>';
                }}
                if (timestamp) {{
                    if (footer) previewHTML += '<span style="margin: 0 4px;">•</span>';
                    const now = new Date();
                    const time = now.toLocaleTimeString('pt-BR', {{ hour: '2-digit', minute: '2-digit' }});
                    previewHTML += '<span>Hoje às ' + time + '</span>';
                }}
                previewHTML += '</div>';
            }}
            
            previewHTML += `
                    </div>
                </div>
                </div>
            </div>
            `;
            
            document.getElementById('embed-preview').innerHTML = previewHTML;
        }}
        
        // Preview da mensagem do vencedor
        function showWinnerPreview() {{
            const template = document.getElementById('embed-template').value;
            if (template !== 'giveaway') return;
            
            const prize = document.getElementById('giveaway-prize').value || 'Não especificado';
            const winners = document.getElementById('giveaway-winners').value || '1';
            const winnerMessage = document.getElementById('giveaway-winner-message').value || '';
            const colorPicker = document.getElementById('embed-color-picker').value;
            
            // Substituir placeholders
            let message = winnerMessage.replace(/\\{{{{prize}}}}/g, prize);
            message = message.replace(/\\{{{{winners}}}}/g, '@Vencedor' + (winners > 1 ? ` +${{parseInt(winners)-1}}` : ''));
            
            // Converter quebras de linha e markdown
            message = message.replace(/\\n/g, '<br>');
            message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            const previewHTML = `
            <style>
                .discord-message {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
                    background: #313338;
                    padding: 16px;
                    border-radius: 4px;
                }}
                .discord-message * {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
                }}
            </style>
            <div class="discord-message">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <img src="https://i.ibb.co/VpPdrYCk/Chat-GPT-Image-11-de-set-de-2025-18-35-32.png" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 12px;">
                    <span style="font-size: 15px; font-weight: 500; color: #f2f3f5; margin-right: 6px;">CAOS Bot</span>
                    <span style="background: #5865f2; color: #fff; font-size: 10px; font-weight: 500; padding: 2px 4px; border-radius: 3px; text-transform: uppercase;">BOT</span>
                </div>
                <div style="margin-left: 52px;">
                    <div style="color: #dbdee1; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">@Vencedor${{winners > 1 ? ` +${{parseInt(winners)-1}}` : ''}}</div>
                    <div style="border-left: 4px solid ${{colorPicker}}; background: #2b2d31; padding: 12px; border-radius: 4px;">
                        <div style="color: #00aff4; font-size: 15px; font-weight: 600; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">🎉 GIVEAWAY ENCERRADO!</div>
                        <div style="color: #dbdee1; font-size: 14px; line-height: 1.5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">
                            ${{message}}
                        </div>
                        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #404249; font-size: 12px; color: #b5bac1; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;">
                            Participantes: 10
                        </div>
                    </div>
                </div>
            </div>
            `;
            
            document.getElementById('embed-preview').innerHTML = previewHTML;
        }}
        
        // Enviar embed
        async function sendEmbed() {{
            const channelId = document.getElementById('embed-channel').value;
            
            if (!channelId) {{
                showToast('❌ Selecione um canal!', 'error');
                return;
            }}
            
            const title = document.getElementById('embed-title').value;
            const description = document.getElementById('embed-description').value;
            
            if (!title && !description) {{
                showToast('❌ Preencha pelo menos o título ou descrição!', 'error');
                return;
            }}
            
            const template = document.getElementById('embed-template').value;
            
            // Coletar todos os dados
            const embedData = {{
                channel_id: channelId,
                title: title,
                description: description,
                color: document.getElementById('embed-color').value,
                image: document.getElementById('embed-image').value,
                thumbnail: document.getElementById('embed-thumbnail').value,
                author: document.getElementById('embed-author').value,
                author_url: document.getElementById('embed-author-url').value,
                footer: document.getElementById('embed-footer').value,
                footer_icon: document.getElementById('embed-footer-icon').value,
                timestamp: document.getElementById('embed-timestamp').checked,
                fields: []
            }};
            
            // Se for giveaway, adicionar dados específicos
            if (template === 'giveaway') {{
                const duration = document.getElementById('giveaway-duration').value || '7';
                const unit = document.getElementById('giveaway-time-unit').value;
                const winners = document.getElementById('giveaway-winners').value || '1';
                const emoji = document.getElementById('giveaway-emoji').value || '🎉';
                const prize = document.getElementById('giveaway-prize').value || 'Prêmio não especificado';
                const winnerMessage = document.getElementById('giveaway-winner-message').value || '';
                
                embedData.giveaway = {{
                    duration: parseInt(duration),
                    time_unit: unit,
                    winners: parseInt(winners),
                    emoji: emoji,
                    prize: prize,
                    winner_message: winnerMessage
                }};
            }}
            
            // Coletar fields
            document.querySelectorAll('.embed-field').forEach(field => {{
                const name = field.querySelector('.field-name').value;
                const value = field.querySelector('.field-value').value;
                const inline = field.querySelector('.field-inline').checked;
                if (name || value) {{
                    embedData.fields.push({{ name: name || 'Campo', value: value || 'Valor', inline }});
                }}
            }});
            
            // Adicionar mensagem extra se tiver
            const extraMessage = document.getElementById('embed-extra-message').value;
            if (extraMessage) {{
                embedData.extra_message = extraMessage;
            }}
            
            try {{
                const apiUrl = template === 'giveaway' ? '/api/embeds/giveaway' : '/api/embeds/send';
                const response = await fetch(apiUrl, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(embedData)
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    showToast('✅ Embed enviado com sucesso!', 'success');
                }} else {{
                    showToast('❌ Erro: ' + data.message, 'error');
                }}
            }} catch (error) {{
                showToast('❌ Erro ao enviar embed!', 'error');
                console.error(error);
            }}
        }}
        
        // Carregar categorias para embed
        async function loadEmbedCategories() {{
            try {{
                const response = await fetch('/api/discord/categories');
                const data = await response.json();
                
                if (data.success) {{
                    const select = document.getElementById('embed-category');
                    select.innerHTML = '<option value="">Todas as categorias</option>';
                    data.categories.forEach(cat => {{
                        select.innerHTML += `<option value="${{cat.id}}">${{cat.name}}</option>`;
                    }});
                    
                    // Carregar todos os canais inicialmente
                    loadAllEmbedChannels();
                }}
            }} catch (error) {{
                console.error('Erro ao carregar categorias:', error);
            }}
        }}
        
        // Carregar todos os canais
        async function loadAllEmbedChannels() {{
            try {{
                const response = await fetch('/api/discord/text-channels');
                const data = await response.json();
                
                if (data.success) {{
                    const select = document.getElementById('embed-channel');
                    select.innerHTML = '<option value="">Selecione um canal...</option>';
                    data.channels.forEach(channel => {{
                        select.innerHTML += `<option value="${{channel.id}}">#${{channel.name}}</option>`;
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar canais:', error);
            }}
        }}
        
        // Carregar canais por categoria
        async function loadEmbedChannelsByCategory() {{
            const categoryId = document.getElementById('embed-category').value;
            
            if (!categoryId) {{
                // Se não selecionou categoria, mostra todos
                loadAllEmbedChannels();
                return;
            }}
            
            try {{
                const response = await fetch(`/api/discord/categories/${{categoryId}}/channels`);
                const data = await response.json();
                
                if (data.success) {{
                    const select = document.getElementById('embed-channel');
                    select.innerHTML = '<option value="">Selecione um canal...</option>';
                    data.channels.forEach(channel => {{
                        select.innerHTML += `<option value="${{channel.id}}">#${{channel.name}}</option>`;
                    }});
                }}
            }} catch (error) {{
                console.error('Erro ao carregar canais da categoria:', error);
            }}
        }}
        
        // Carregar perfil ao iniciar
        loadUserProfile();
        
        // Carregar categorias quando abrir página de embeds
        const originalShowPage = showPage;
        showPage = function(page) {{
            originalShowPage(page);
            if (page === 'embeds') {{
                loadEmbedCategories();
            }}
        }};
    </script>
</body>
</html>
        """
        return html
    except Exception as e:
        return f"Erro ao carregar dashboard: {e}", 500

@app.route('/api/config/status', methods=['GET'])
def get_config_status():
    """Retorna status atual das configurações"""
    try:
        config = load_config_dashboard()
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/toggle', methods=['POST'])
def toggle_config_api():
    """Alterna estado de uma configuração"""
    try:
        data = request.get_json()
        key = data.get('key')
        
        if not key:
            return jsonify({'success': False, 'message': 'Key não fornecida'}), 400
        
        config = load_config_dashboard()
        
        if key not in config:
            return jsonify({'success': False, 'message': 'Key inválida'}), 400
        
        # Alternar estado
        config[key] = not config[key]
        save_config_dashboard(config)
        
        return jsonify({
            'success': True,
            'key': key,
            'new_value': config[key],
            'message': f'{key} agora está {"ativado" if config[key] else "desativado"}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/config/update', methods=['POST'])
def update_config_api():
    """Atualiza múltiplas configurações de uma vez"""
    try:
        data = request.get_json()
        config = load_config_dashboard()
        
        # Atualizar apenas chaves válidas
        valid_keys = ['welcome_enabled', 'goodbye_enabled', 'autorole_enabled', 'tickets_enabled']
        updated = []
        
        for key in valid_keys:
            if key in data:
                config[key] = bool(data[key])
                updated.append(key)
        
        save_config_dashboard(config)
        
        return jsonify({
            'success': True,
            'updated': updated,
            'config': config,
            'message': f'{len(updated)} configurações atualizadas'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def load_config_dashboard():
    """Carrega configurações do dashboard"""
    default_config = {
        'welcome_enabled': False,
        'goodbye_enabled': False,
        'autorole_enabled': False,
        'tickets_enabled': False,
        'status_message_id': None
    }
    
    if os.path.exists(WELCOME_CONFIG_FILE):
        try:
            with open(WELCOME_CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("⚠️ Arquivo de config vazio, usando padrões")
                    return default_config
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido no arquivo de config: {e}")
            print(f"🔧 Recriando arquivo com configs padrão...")
            # Deletar arquivo corrompido e criar novo
            try:
                os.remove(WELCOME_CONFIG_FILE)
            except:
                pass
            save_config_dashboard(default_config)
            return default_config
        except Exception as e:
            print(f"❌ Erro ao ler config: {e}")
            return default_config
    
    return default_config

def save_config_dashboard(config):
    """Salva configurações do dashboard"""
    try:
        with open(WELCOME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configurações salvas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações: {e}")

# ========================================
# ENDPOINTS DO SISTEMA DE TICKETS
# ========================================

@app.route('/api/discord/channels', methods=['GET'])
def get_discord_channels():
    """Retorna lista de canais do Discord"""
    try:
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]  # Primeiro servidor
        channels = []
        
        for channel in guild.text_channels:
            channels.append({
                'id': str(channel.id),
                'name': channel.name,
                'category': channel.category.name if channel.category else 'Sem categoria'
            })
        
        return jsonify({'success': True, 'channels': channels})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discord/categories', methods=['GET'])
def get_discord_categories():
    """Retorna lista de categorias do Discord"""
    try:
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]
        categories = []
        
        for category in guild.categories:
            categories.append({
                'id': str(category.id),
                'name': category.name
            })
        
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tickets/config', methods=['GET'])
def get_ticket_config_route():
    """Retorna configuração completa de tickets"""
    try:
        guild_id = request.args.get('guild_id')
        if not guild_id:
            return jsonify({'success': False, 'message': 'Guild ID não especificado'}), 400
        
        # Se não existe config, retorna padrão
        if guild_id not in ticket_config:
            config = get_default_ticket_config(guild_id)
        else:
            config = ticket_config[guild_id]
        
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tickets/config', methods=['POST'])
def save_ticket_config_route():
    """Salva configuração completa de tickets"""
    try:
        data = request.json
        guild_id = data.get('guild_id')
        config = data.get('config')
        
        if not guild_id or not config:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Salvar configuração
        ticket_config[guild_id] = config
        save_ticket_config()
        
        return jsonify({'success': True, 'message': 'Configuração salva com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tickets/panel/send', methods=['POST'])
def send_ticket_panel():
    """Envia painel de ticket COMPLETO com categorias"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        category_id = data.get('category_id')
        log_channel_id = data.get('log_channel_id')
        staff_roles = data.get('staff_roles', [])  # Array de IDs de staff
        title = data.get('title', '🎫 SISTEMA DE TICKETS')
        description = data.get('description', 'Selecione uma categoria abaixo para abrir um ticket!')
        color = data.get('color', '0x5865F2')
        
        if not channel_id:
            return jsonify({'success': False, 'message': 'Canal não especificado'}), 400
        
        # SALVAR CONFIGURAÇÃO (category_id, log_channel_id, staff_roles)
        if bot.guilds:
            guild_id = str(bot.guilds[0].id)
            ticket_config[guild_id] = {
                'category_id': category_id,
                'log_channel_id': log_channel_id,
                'staff_roles': staff_roles,
                'max_tickets_per_user': ticket_config.get(guild_id, {}).get('max_tickets_per_user', 1)
            }
            # Salvar no arquivo
            save_ticket_config()
        
        # Agendar envio do painel
        async def send_panel():
            try:
                channel = bot.get_channel(int(channel_id))
                if not channel:
                    return False
                
                # EMBED LIMPO (sem lista de categorias - aparecem no dropdown)
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=int(color, 16) if isinstance(color, str) else color
                )
                embed.set_footer(text='Sistema de Tickets • Caos Hub')
                
                # Usar o novo sistema de BOTÃO (abre dropdowns ephemeral)
                view = TicketPanelView()
                
                await channel.send(embed=embed, view=view)
                return True
            except Exception as e:
                print(f'Erro ao enviar painel: {e}')
                return False
        
        # Executar
        future = asyncio.run_coroutine_threadsafe(send_panel(), bot.loop)
        result = future.result(timeout=10)
        
        if result:
            return jsonify({'success': True, 'message': 'Painel enviado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao enviar painel'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discord/channels/<category_id>', methods=['GET'])
def get_category_channels(category_id):
    """Retorna canais de uma categoria específica"""
    try:
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]
        category = guild.get_channel(int(category_id))
        
        if not category:
            return jsonify({'success': False, 'message': 'Categoria não encontrada'}), 404
        
        channels = []
        for channel in category.text_channels:
            channels.append({
                'id': str(channel.id),
                'name': channel.name
            })
        
        return jsonify({'success': True, 'channels': channels})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/embeds/send', methods=['POST'])
def send_embed():
    """Envia embed customizado para um canal"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        
        if not channel_id:
            return jsonify({'success': False, 'message': 'Canal não especificado'}), 400
        
        # Criar embed
        embed_dict = {}
        
        if data.get('title'):
            embed_dict['title'] = data['title']
        
        if data.get('description'):
            embed_dict['description'] = data['description']
        
        if data.get('color'):
            try:
                color_hex = data['color'].replace('0x', '')
                embed_dict['color'] = int(color_hex, 16)
            except:
                embed_dict['color'] = 0xff6600
        
        if data.get('image'):
            embed_dict['image'] = {'url': data['image']}
        
        if data.get('thumbnail'):
            embed_dict['thumbnail'] = {'url': data['thumbnail']}
        
        if data.get('author'):
            author_dict = {'name': data['author']}
            if data.get('author_url'):
                author_dict['url'] = data['author_url']
            embed_dict['author'] = author_dict
        
        if data.get('footer'):
            footer_dict = {'text': data['footer']}
            if data.get('footer_icon'):
                footer_dict['icon_url'] = data['footer_icon']
            embed_dict['footer'] = footer_dict
        
        if data.get('timestamp'):
            from datetime import datetime
            embed_dict['timestamp'] = datetime.utcnow().isoformat()
        
        if data.get('fields'):
            embed_dict['fields'] = []
            for field in data['fields']:
                embed_dict['fields'].append({
                    'name': field.get('name', 'Campo'),
                    'value': field.get('value', 'Valor'),
                    'inline': field.get('inline', False)
                })
        
        # Enviar embed de forma assíncrona
        async def send_embed_async():
            try:
                channel = bot.get_channel(int(channel_id))
                if not channel:
                    return False, 'Canal não encontrado'
                
                embed = discord.Embed.from_dict(embed_dict)
                
                # Enviar com mensagem extra se tiver
                extra_msg = data.get('extra_message', '')
                if extra_msg:
                    await channel.send(content=extra_msg, embed=embed)
                else:
                    await channel.send(embed=embed)
                
                return True, 'Embed enviado'
            except Exception as e:
                return False, str(e)
        
        future = asyncio.run_coroutine_threadsafe(send_embed_async(), bot.loop)
        success, message = future.result(timeout=10)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        print(f'❌ Erro ao enviar embed: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/embeds/giveaway', methods=['POST'])
def send_giveaway():
    """Envia giveaway com reação e sorteio automático"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        giveaway_data = data.get('giveaway', {})
        
        if not channel_id:
            return jsonify({'success': False, 'message': 'Canal não especificado'}), 400
        
        if not giveaway_data:
            return jsonify({'success': False, 'message': 'Dados do giveaway não especificados'}), 400
        
        # Criar embed
        embed_dict = {}
        
        if data.get('title'):
            embed_dict['title'] = data['title']
        
        if data.get('description'):
            embed_dict['description'] = data['description']
        
        if data.get('color'):
            try:
                color_hex = data['color'].replace('0x', '')
                embed_dict['color'] = int(color_hex, 16)
            except:
                embed_dict['color'] = 0xe91e63
        
        if data.get('footer'):
            embed_dict['footer'] = {'text': data['footer']}
        
        if data.get('timestamp'):
            from datetime import datetime, timedelta
            
            # Calcular tempo de fim
            duration = giveaway_data.get('duration', 7)
            time_unit = giveaway_data.get('time_unit', 'd')
            
            if time_unit == 'm':
                end_time = datetime.utcnow() + timedelta(minutes=duration)
            elif time_unit == 'h':
                end_time = datetime.utcnow() + timedelta(hours=duration)
            else:  # dias
                end_time = datetime.utcnow() + timedelta(days=duration)
            
            embed_dict['timestamp'] = end_time.isoformat()
        
        # Enviar embed e adicionar reação
        async def send_giveaway_async():
            try:
                channel = bot.get_channel(int(channel_id))
                if not channel:
                    return False, 'Canal não encontrado'
                
                embed = discord.Embed.from_dict(embed_dict)
                
                # Enviar com mensagem extra se tiver (JUNTO, não separado)
                extra_msg = data.get('extra_message', '')
                if extra_msg:
                    message = await channel.send(content=extra_msg, embed=embed)
                else:
                    message = await channel.send(embed=embed)
                
                # Adicionar reação
                emoji = giveaway_data.get('emoji', '🎉')
                try:
                    await message.add_reaction(emoji)
                except:
                    await message.add_reaction('🎉')  # Fallback
                    emoji = '🎉'
                
                # Agendar sorteio automático
                duration = giveaway_data.get('duration', 7)
                time_unit = giveaway_data.get('time_unit', 'd')
                winners_count = giveaway_data.get('winners', 1)
                prize = giveaway_data.get('prize', 'Prêmio')
                
                # Calcular tempo em segundos
                if time_unit == 'm':
                    wait_time = duration * 60
                elif time_unit == 'h':
                    wait_time = duration * 3600
                else:  # dias
                    wait_time = duration * 86400
                
                # Agendar task para sortear depois
                async def do_giveaway_draw():
                    await asyncio.sleep(wait_time)
                    
                    # Refetch da mensagem para pegar reações atualizadas
                    try:
                        msg = await channel.fetch_message(message.id)
                        
                        # Pegar usuários que reagiram
                        reaction = None
                        for r in msg.reactions:
                            if str(r.emoji) == emoji:
                                reaction = r
                                break
                        
                        if not reaction or reaction.count <= 1:  # Só o bot
                            await channel.send(f"🎉 **SORTEIO ENCERRADO**\n\nNinguém participou do sorteio de **{prize}**! 😢")
                            return
                        
                        # Pegar participantes (excluindo o bot)
                        participants = []
                        async for user in reaction.users():
                            if not user.bot:
                                participants.append(user)
                        
                        if len(participants) == 0:
                            await channel.send(f"🎉 **SORTEIO ENCERRADO**\n\nNinguém participou do sorteio de **{prize}**! 😢")
                            return
                        
                        # Sortear vencedores
                        import random
                        actual_winners = min(winners_count, len(participants))
                        winners = random.sample(participants, actual_winners)
                        
                        # Anunciar vencedores
                        winners_mention = ', '.join([w.mention for w in winners])
                        
                        # Usar mensagem customizável
                        winner_msg_template = giveaway_data.get('winner_message', '🎊 **Parabéns!** 🎊\n\nVocê ganhou **{prize}**!\n\n📋 Abra um ticket na categoria 🎉 **Sorteios** para receber seu prêmio.')
                        winner_description = winner_msg_template.replace('{prize}', prize).replace('{winners}', winners_mention)
                        
                        result_embed = discord.Embed(
                            title="🎉 GIVEAWAY ENCERRADO!",
                            description=winner_description,
                            color=0x00ff00
                        )
                        result_embed.set_footer(text=f"Participantes: {len(participants)}")
                        
                        await channel.send(content=winners_mention, embed=result_embed)
                        
                    except Exception as e:
                        print(f"❌ Erro ao sortear giveaway: {e}")
                        await channel.send(f"❌ Erro ao realizar sorteio! Contate um administrador.")
                
                # Criar task
                bot.loop.create_task(do_giveaway_draw())
                
                return True, f'Giveaway criado! ID: {message.id}'
            except Exception as e:
                return False, str(e)
        
        future = asyncio.run_coroutine_threadsafe(send_giveaway_async(), bot.loop)
        success, message = future.result(timeout=10)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        print(f'❌ Erro ao criar giveaway: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discord/text-channels', methods=['GET'])
def get_all_text_channels():
    """Retorna todos os canais de texto do servidor"""
    try:
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]
        channels = []
        
        for channel in guild.text_channels:
            channels.append({
                'id': str(channel.id),
                'name': channel.name
            })
        
        return jsonify({'success': True, 'channels': channels})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discord/roles', methods=['GET'])
def get_discord_roles():
    """Retorna APENAS os cargos de STAFF (moderação)"""
    # IDs dos cargos de staff (só esses aparecem no dropdown)
    STAFF_ROLE_IDS = [
        1365636960651051069,  # 🔥 Founder [FND]
        1365636456386789437,  # 🌟 Sub Dono [SDN]
        1365633918593794079,  # 👑 Administrador [ADM]
        1365634226254254150,  # 🛠️ Staff [STF]
        1365633102973763595,  # ⚔️ Moderador [MOD]
        1365631940434333748,  # 🛡️ Sub Moderador [SBM]
    ]
    
    try:
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]
        roles = []
        
        # Filtrar APENAS os cargos de staff
        for role in guild.roles:
            if role.id in STAFF_ROLE_IDS:
                roles.append({
                    'id': str(role.id),
                    'name': role.name,
                    'color': str(role.color)
                })
        
        # Ordenar na hierarquia (mesma ordem do array STAFF_ROLE_IDS)
        roles.sort(key=lambda r: STAFF_ROLE_IDS.index(int(r['id'])))
        
        return jsonify({'success': True, 'roles': roles})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Verifica se usuário ainda tem permissões (para polling em tempo real)"""
    try:
        if 'user' not in session:
            return jsonify({'authorized': False, 'reason': 'not_logged_in'}), 401
        
        user_id = session['user']['id']
        has_permission = check_user_permissions(user_id)
        
        if not has_permission:
            session.clear()
            return jsonify({'authorized': False, 'reason': 'permission_revoked'}), 403
        
        return jsonify({'authorized': True}), 200
    except Exception as e:
        return jsonify({'authorized': False, 'reason': str(e)}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Retorna perfil do usuário logado"""
    try:
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        user = session['user']
        user_id = user.get('id')
        
        # Buscar cargo do usuário no servidor
        if not bot.guilds:
            return jsonify({'success': False, 'message': 'Bot não conectado'}), 500
        
        guild = bot.guilds[0]
        member = guild.get_member(int(user_id))
        
        role_name = 'Administrador'
        if member:
            # IDs dos cargos (mesmo ordem do código)
            if '1365636960651051069' in [str(r.id) for r in member.roles]:
                role_name = '👑 Founder'
            elif '1365636456386789437' in [str(r.id) for r in member.roles]:
                role_name = '⚡ Sub-Dono'
            elif '1365633918593794079' in [str(r.id) for r in member.roles]:
                role_name = '🛡️ Administrador'
        
        return jsonify({
            'success': True,
            'username': user.get('username'),
            'avatar': user.get('avatar'),
            'role': role_name
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def get_current_stats():
    """Helper para obter estatísticas atuais"""
    try:
        if not bot.guilds:
            return None
        
        guild = bot.guilds[0]
        
        # Separar humanos e bots
        humans = [m for m in guild.members if not m.bot]
        bots = [m for m in guild.members if m.bot]
        
        # Contar online separado (online, idle, dnd = considerados online)
        humans_online = sum(1 for m in humans if m.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd])
        bots_online = sum(1 for m in bots if m.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd])
        
        return {
            'success': True,
            'server_name': guild.name,
            'server_icon': str(guild.icon.url) if guild.icon else None,
            'total_members': guild.member_count,
            'total_humans': len(humans),
            'total_bots': len(bots),
            'humans_online': humans_online,
            'bots_online': bots_online,
            'online_members': humans_online + bots_online,
            'total_channels': len(guild.channels),
            'text_channels': len(guild.text_channels),
            'voice_channels': len(guild.voice_channels),
            'total_roles': len(guild.roles),
            'boost_level': guild.premium_tier,
            'boost_count': guild.premium_subscription_count,
            'created_at': guild.created_at.strftime('%Y-%m-%d')
        }
    except:
        return None

@app.route('/api/server/stats', methods=['GET'])
def get_server_stats():
    """Retorna estatísticas do servidor"""
    stats = get_current_stats()
    if stats:
        return jsonify(stats)
    return jsonify({'success': False, 'message': 'Bot não conectado'}), 500

@app.route('/api/server/stats/stream')
def stats_stream():
    """Stream de estatísticas em tempo real via SSE"""
    def generate():
        import time
        import json
        last_stats = None
        while True:
            try:
                stats = get_current_stats()
                if stats and stats != last_stats:
                    yield f"data: {json.dumps(stats)}\n\n"
                    last_stats = stats
                time.sleep(2)  # Atualiza a cada 2 segundos
            except:
                pass
    
    return Response(generate(), mimetype='text/event-stream')

def run_web():
    import os
    try:
        port = int(os.getenv("PORT", 10000))
        print(f'🌐 Servidor HTTP iniciado na porta {port}')
        print(f'🔧 REDIRECT_URI: {DISCORD_REDIRECT_URI}')
        print(f'🔧 CLIENT_ID: {DISCORD_CLIENT_ID}')
        print(f'📍 Rotas disponíveis:')
        print(f'   - http://0.0.0.0:{port}/')
        print(f'   - http://0.0.0.0:{port}/test')
        print(f'   - http://0.0.0.0:{port}/ping')
        print(f'   - http://0.0.0.0:{port}/login')
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f'❌ ERRO AO INICIAR FLASK: {e}')
        import traceback
        traceback.print_exc()

# NÃO inicia aqui! Vai iniciar no bloco if __name__ == '__main__'

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # NECESSÁRIO para eventos de entrada/saída/ban
intents.presences = True  # NECESSÁRIO para ver status online/offline dos membros

# Bot configurado com PREFIXO (.)
bot = commands.Bot(command_prefix='.', intents=intents)

            description=f"**Criado por:** {member.mention}\n**Categoria:** {category_name}",
            color=0x5865F2,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📋 Assunto", value=assunto, inline=False)
        embed.add_field(name="📝 Descrição", value=descricao, inline=False)
        embed.add_field(name="🔢 Número do Ticket", value=f"`#{ticket_number}`", inline=True)
        embed.add_field(name="⏰ Status", value="🟢 Aguardando atendimento", inline=True)
        embed.set_footer(text=f"Sistema de Tickets • Caos Hub | Ticket {ticket_name}")
        
        # Enviar com botões de gerenciamento
        await ticket_channel.send(f"{member.mention}", embed=embed, view=TicketManageView(ticket_channel))
        
        # Responder
        await interaction.followup.send(
            f'✅ Ticket criado com sucesso! {ticket_channel.mention}',
            ephemeral=True
        )
        
    except Exception as e:
        print(f'❌ Erro ao criar ticket: {e}')
        try:
            await interaction.followup.send('❌ Erro ao criar ticket. Contate um administrador.', ephemeral=True)
        except:
            pass

async def handle_create_ticket(interaction: discord.Interaction):
    """Handler antigo - redireciona para novo sistema"""
    # Agora não usa mais - substituído pelo sistema de categorias
    pass

# Nova função COMPLETA com todos os campos
async def create_ticket_channel_complete(interaction, category_name, category_emoji, priority_name, priority_emoji, assunto, descricao, idioma, info_adicional):
    """Cria canal de ticket COMPLETO igual da imagem"""
    try:
        guild = interaction.guild
        member = interaction.user
        
        # Verificar quantos tickets o usuário já tem abertos
        user_tickets = [ch for ch in guild.text_channels if f'Ticket de {member.id}' in (ch.topic or '')]
        max_tickets = ticket_config.get('max_tickets_per_user', 1)  # Padrão: 1 ticket
        
        if len(user_tickets) >= max_tickets:
            await interaction.response.send_message(
                f'❌ Você já possui {len(user_tickets)} ticket(s) aberto(s). Limite: {max_tickets}\n' +
                (f'Ticket: {user_tickets[0].mention}' if len(user_tickets) == 1 else 
                 f'Tickets: {", ".join([t.mention for t in user_tickets])}'),
                ephemeral=True
            )
            return
        
        # Categoria STUFF (hardcoded)
        ticket_category = guild.get_channel(1365692340651556894)
        
        # Se não encontrou, usar padrão
        if not ticket_category:
            ticket_category = discord.utils.get(guild.categories, name='📂 TICKETS')
            if not ticket_category:
                ticket_category = await guild.create_category('📂 TICKETS')
        
        # Mapear nomes curtos
        category_map = {
            "Geral": "geral", "Compras": "compras", "Suporte Técnico": "suporte",
            "Denúncia": "denuncia", "Parceria": "parceria", "Financeiro": "financeiro",
            "Moderação": "moderacao", "Bug": "bug",
        }
        
        # Incrementar contador
        category_short = category_map.get(category_name, "ticket")
        ticket_counters[category_short] += 1
        ticket_number = ticket_counters[category_short]
        
        # Nome: emoji-categoria-numero
        ticket_name = f'{category_emoji}-{category_short}-{ticket_number}'
        
        # ===== CONFIGURAR PERMISSÕES NA CRIAÇÃO =====
        guild_id = str(guild.id)
        config = ticket_config.get(guild_id, {})
        selected_staff_roles = config.get('staff_roles', [])
        
        # Criar overwrites (permissões do canal)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Bloquear @everyone
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True)  # Liberar usuário
        }
        
        # Adicionar APENAS os staff roles SELECIONADOS
        for role_id in selected_staff_roles:
            role = guild.get_role(int(role_id))
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_messages=True
                )
        
        # Criar canal COM as permissões já definidas (não herda da categoria)
        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=ticket_category,
            topic=f'Ticket de {member.id} | {category_name} #{ticket_number}',
            overwrites=overwrites  # ← ISSO É CRUCIAL!
        )
        
        # Cor baseada na prioridade
        priority_colors = {"Baixa": 0x00ff00, "Média": 0xffff00, "Alta": 0xff8800, "Urgente": 0xff0000}
        embed_color = priority_colors.get(priority_name, 0x5865F2)
        
        # EMBED COMPLETO
        embed = discord.Embed(
            title=f"{category_emoji} Ticket de {member.display_name}",
            description=f"**🎫 NOVO TICKET ABERTO**\n\n*Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.*\n\n*Nossa equipe responderá o mais breve possível!*",
            color=embed_color,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="👤 Aberto por", value=f"{member.mention}\n**ID:** `{member.id}`", inline=True)
        embed.add_field(name=f"{category_emoji} Categoria", value=f"{category_emoji} {category_name}", inline=True)
        embed.add_field(name=f"{priority_emoji} Prioridade", value=f"{priority_emoji} {priority_name}", inline=True)
        embed.add_field(name="🌐 Idioma", value=idioma, inline=False)
        embed.add_field(name="📄 Assunto", value=f"```\n{assunto}\n```", inline=False)
        embed.add_field(name="📝 Descrição Detalhada", value=f"```\n{descricao}\n```", inline=False)
        embed.add_field(name="ℹ️ Informações Adicionais", value=f"```\n{info_adicional}\n```", inline=False)
        embed.set_footer(text=f"Sistema de Tickets • Caos Hub • Hoje às {discord.utils.utcnow().strftime('%I:%M %p')}")
        
        # Enviar mensagem no canal do ticket
        await ticket_channel.send(f"{member.mention}", embed=embed, view=TicketManageView(ticket_channel))
        
        # LOG
        log_channel = discord.utils.get(guild.text_channels, name='ticket-logs')
        if log_channel:
            log_embed = discord.Embed(title="🎫 NOVO TICKET", description=f"Ticket `{ticket_name}` criado", color=0x00ff00, timestamp=discord.utils.utcnow())
            log_embed.add_field(name="Canal", value=ticket_channel.mention, inline=True)
            log_embed.add_field(name="Usuário", value=member.mention, inline=True)
            log_embed.add_field(name="Categoria", value=f"{category_emoji} {category_name}", inline=True)
            log_embed.add_field(name="Prioridade", value=f"{priority_emoji} {priority_name}", inline=True)
            await log_channel.send(embed=log_embed)
        
        # RETORNAR o canal criado
        return ticket_channel
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return None

# ========================================
# EVENTOS DE BOAS-VINDAS/SAÍDA/BAN
# ========================================

@bot.event
async def on_member_join(member):
    """Evento quando alguém entra no servidor - CONTROLADO PELO DASHBOARD + ANTI-RAID"""
    try:
        guild = member.guild
        current_time = time.time()
        
        # ========================================
        # SISTEMA ANTI-RAID - VERIFICAÇÃO DE ENTRADA
        # ========================================
        
        # Adicionar entrada ao histórico
        raid_detection['recent_joins'].append(current_time)
        
        # Verificar se é usuário suspeito
        is_suspicious, suspicion_reason = await check_suspicious_user(member)
        
        # SE ESTÁ EM MODO RAID + usuário suspeito = BAN IMEDIATO
        if raid_detection['in_raid_mode'] and is_suspicious:
            try:
                await member.ban(reason=f"[ANTI-RAID] {suspicion_reason}")
                raid_detection['auto_banned'].add(member.id)
                print(f"🚨 [ANTI-RAID] Banido: {member.name} - {suspicion_reason}")
                
                # Log
                log_channel = guild.get_channel(1315107491453444137)
                if log_channel:
                    embed = discord.Embed(
                        title="🚨 AUTO-BAN (MODO RAID)",
                        description=f"**{member.name}** foi banido automaticamente.",
                        color=0xFF0000,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.add_field(name="👤 Usuário", value=f"{member.mention}\nID: `{member.id}`", inline=True)
                    embed.add_field(name="🔍 Motivo", value=suspicion_reason, inline=True)
                    embed.set_footer(text="Sistema Anti-Raid • Caos Hub")
                    await log_channel.send(embed=embed)
                
                return  # Para o processamento
            except Exception as e:
                print(f"❌ Erro ao banir raider: {e}")
        
        # Verificar padrão de raid (muitas entradas)
        if await check_raid_pattern(guild):
            # Ativar modo raid se não estiver ativo
            if not raid_detection['in_raid_mode']:
                asyncio.create_task(activate_raid_mode(guild))
        
        # Adicionar à lista de suspeitos se for suspeito (mesmo sem raid mode)
        if is_suspicious:
            raid_detection['suspicious_users'].add(member.id)
            print(f"⚠️ Usuário suspeito detectado: {member.name} - {suspicion_reason}")
        
        print(f"\n{'='*50}")
        print(f"📥 NOVO MEMBRO DETECTADO: {member.name}")
        print(f"{'='*50}")
        print(f"🔍 DEBUG - Configurações atuais:")
        print(f"   welcome_config completo: {welcome_config}")
        print(f"   welcome_enabled: {is_on('welcome_enabled')}")
        print(f"   autorole_enabled: {is_on('autorole_enabled')}")
        print(f"   Tipo de welcome_enabled: {type(welcome_config.get('welcome_enabled'))}")
        
        # AUTOROLE - Verificação INTELIGENTE
        if is_on('autorole_enabled'):
            print(f"   ✅ Autorole ATIVADO - Dando cargo...")
            role = member.guild.get_role(AUTOROLE_ID)
            if role:
                await member.add_roles(role)
                print(f"   ✅ Cargo {role.name} adicionado a {member.name}")
            else:
                print(f"   ⚠️ Cargo de autorole não encontrado!")
        else:
            print(f"   ❌ Autorole DESATIVADO - Pulando...")
        
        # BOAS-VINDAS - Verificação INTELIGENTE
        print(f"\n🎯 VERIFICANDO TOGGLE DE BOAS-VINDAS...")
        print(f"   Valor de welcome_enabled: {welcome_config.get('welcome_enabled')}")
        print(f"   Condição normalizada: {is_on('welcome_enabled')}")
        
        if is_on('welcome_enabled'):
            print(f"   ✅ TOGGLE ATIVADO - Enviando mensagem de boas-vindas!")
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
                print(f"   ✅ Boas-vindas enviadas para {member.name}")
            else:
                print(f"   ⚠️ Canal de boas-vindas não encontrado!")
        else:
            print(f"   ❌ TOGGLE DESATIVADO - NÃO enviando mensagem!")
            print(f"   🎉 Sistema funcionando corretamente - toggle respeitado!")
        
        print(f"{'='*50}\n")
                
    except Exception as e:
        print(f"❌ Erro no evento de entrada: {e}")

@bot.event
async def on_member_remove(member):
    """Evento quando alguém sai do servidor - CONTROLADO PELO DASHBOARD"""
    try:
        print(f"📤 Membro saiu: {member.name}")
        print(f"   Estado atual - Goodbye: {is_on('goodbye_enabled')}")
        
        if is_on('goodbye_enabled'):
            print(f"   ✅ Goodbye ATIVADO - Verificando se foi banimento...")
            
            # Verificar se o usuário foi banido (não mostrar mensagem de saída se foi ban)
            try:
                await member.guild.fetch_ban(member)
                # Se chegou aqui, o usuário foi banido - NÃO mostrar mensagem de saída
                print(f"   🔨 {member.name} foi BANIDO - Pulando mensagem de saída")
                return
            except:
                # Usuário não foi banido, mostrar mensagem de saída normal
                print(f"   ➡️ {member.name} SAIU (não foi ban) - Enviando mensagem...")
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
                print(f"   ✅ Mensagem de saída enviada para {member.name}")
            else:
                print(f"   ⚠️ Canal de saída não encontrado!")
        else:
            print(f"   ❌ Goodbye DESATIVADO - Pulando...")
                
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
    """Sistema de moderação automática COMPLETO + bloqueio de comandos + XP"""
    # Ignorar mensagens do próprio bot
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    # ========================================
    # SISTEMA DE XP (ESTILO LORITTA)
    # ========================================
    if message.guild:  # Só em servidores
        user_key = f"{message.author.id}_{message.guild.id}"
        current_time = time.time()
        
        # Verifica cooldown (padrão 60 segundos)
        if user_key not in xp_cooldowns or current_time - xp_cooldowns[user_key] >= 60:
            xp_cooldowns[user_key] = current_time
            
            # Ganha XP aleatório entre 15-25 (tipo Loritta)
            xp_gain = random.randint(15, 25)
            result = add_xp(message.author.id, message.guild.id, xp_gain)
            
            # Se subiu de nível, envia notificação
            if result['level_up']:
                try:
                    # Embed de level up
                    embed = discord.Embed(
                        title="🎉 LEVEL UP!",
                        description=f"Parabéns {message.author.mention}!\nVocê subiu para o **Nível {result['new_level']}**! 🔥",
                        color=0xff6600
                    )
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    
                    await message.channel.send(embed=embed, delete_after=10)
                    
                    # Sistema de cargos automáticos por nível
                    conn = sqlite3.connect('xp_database.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT role_id FROM level_roles WHERE guild_id = ? AND level = ?', 
                                 (str(message.guild.id), result['new_level']))
                    role_result = cursor.fetchone()
                    conn.close()
                    
                    if role_result:
                        role = message.guild.get_role(int(role_result[0]))
                        if role:
                            await message.author.add_roles(role)
                            print(f'🎖️ Cargo {role.name} adicionado a {message.author.name} (Nível {result["new_level"]})')
                except Exception as e:
                    print(f'❌ Erro ao enviar level up: {e}')
    
    # ========================================
    # RESPOSTA QUANDO O BOT É MENCIONADO
    # ========================================
    
    # Verificar se o bot foi mencionado diretamente (sem comando)
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        # Remover menções do bot da mensagem
        content_without_mentions = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        # Só responde se:
        # 1. Não tem nada depois da menção OU
        # 2. Não começa com ponto (comando) OU
        # 3. Não tem outro @mention (tipo .ship @user @user)
        has_command = content_without_mentions.startswith('.')
        has_other_mention = '<@' in content_without_mentions
        
        if not content_without_mentions or (not has_command and not has_other_mention):
            embed = discord.Embed(
                title='👋 Olá! Eu sou o CAOS Bot!',
                description=f'Oi **{message.author.mention}**! Precisa de ajuda?\n\n'
                           f'Use o comando **`.help`** para ver todos os meus comandos!',
                color=0xff6600
            )
            embed.set_footer(
                text=f'Prefixo: . (ponto) • Digite .help para mais informações',
                icon_url=bot.user.display_avatar.url
            )
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            
            await message.reply(embed=embed)
            return
    
    # ========================================
    # BLOQUEIO DE COMANDOS DE MÚSICA EM CALLS PROTEGIDAS
    # ========================================
    
    music_commands = ['m!p', 'm!play', 'm!join', 'm!summon', 'm!connect']
    message_lower = message.content.lower()
    is_music_command = any(message_lower.startswith(cmd) for cmd in music_commands)
    
    if is_music_command:
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
            if voice_channel.id in PROTECTED_VOICE_CHANNELS:
                try:
                    await message.delete()
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
    
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return
    
    # ========================================
    # SISTEMA ANTI-RAID - DETECÇÃO DE FLOOD GLOBAL
    # ========================================
    
    # Adicionar mensagem ao histórico global
    raid_detection['recent_messages'].append(time.time())
    
    # Verificar flood de mensagens no servidor
    if await check_message_flood(message.guild):
        if not raid_detection['in_raid_mode']:
            asyncio.create_task(activate_raid_mode(message.guild))
    
    # SE USUÁRIO SUSPEITO ENVIAR MENSAGEM EM MODO RAID = BAN
    if raid_detection['in_raid_mode'] and message.author.id in raid_detection['suspicious_users']:
        try:
            await message.author.ban(reason="[ANTI-RAID] Usuário suspeito enviando mensagens durante raid")
            raid_detection['auto_banned'].add(message.author.id)
            raid_detection['suspicious_users'].discard(message.author.id)
            print(f"🚨 [ANTI-RAID] Banido: {message.author.name} - Atividade suspeita em raid")
            return
        except:
            pass
    
    # ========================================
    # SISTEMA ANTI-SPAM E ANTI-FLOOD ATIVADO
    # ========================================
    
    user_id = message.author.id
    current_time = time.time()
    content = message.content
    
    # ANTI-MENÇÃO (máximo 1 menção)
    mention_count = len(message.raw_mentions) + len(message.raw_role_mentions)
    if mention_count >= 2:
        try:
            await message.delete()
        except:
            pass
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
        return
    
    # Adicionar ao histórico
    message_history[user_id].append(content.lower())
    user_message_times[user_id].append(current_time)
    
    # ANTI-SPAM (mensagens idênticas)
    if len(message_history[user_id]) >= 3:
        recent_messages = list(message_history[user_id])[-3:]
        if len(set(recent_messages)) == 1:
            await auto_moderate_spam(message, "spam de mensagens idênticas", f"Enviou 3 mensagens iguais: '{content[:50]}...'")
            return
    
    # ANTI-FLOOD (muitas mensagens rápidas)
    current_warnings = spam_warnings[user_id]
    flood_limit = 5 if current_warnings == 0 else (4 if current_warnings == 1 else 3)
    
    if len(user_message_times[user_id]) >= flood_limit:
        recent_times = list(user_message_times[user_id])[-flood_limit:]
        time_diff = recent_times[-1] - recent_times[0]
        if time_diff < 8:
            await auto_moderate_spam(message, "flood de mensagens", f"Enviou {flood_limit} mensagens em {time_diff:.1f} segundos")
            return
    
    # ANTI-CAPS (excesso de maiúsculas)
    if len(content) > 10:
        uppercase_count = sum(1 for c in content if c.isupper())
        total_letters = sum(1 for c in content if c.isalpha())
        if total_letters > 0:
            caps_percentage = (uppercase_count / total_letters) * 100
            if caps_percentage > 70 and total_letters > 15:
                await auto_moderate_spam(message, "excesso de maiúsculas", f"Mensagem com {caps_percentage:.1f}% em maiúsculas")
                return
    
    # ANTI-MENSAGEM LONGA (máximo 90 caracteres)
    if len(content) > 90:
        await auto_moderate_spam(message, "mensagem muito longa", f"Mensagem com {len(content)} caracteres (máximo: 90)")
        return
    
    # ANTI-EMOJI SPAM
    import re
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿☀-⛿✀-➿]')
    unicode_emojis = len(emoji_pattern.findall(content))
    custom_emojis = content.count('<:') + content.count('<a:')
    total_emojis = unicode_emojis + custom_emojis
    if total_emojis > 10:
        await auto_moderate_spam(message, "spam de emojis", f"Enviou {total_emojis} emojis em uma mensagem")
        return
    
    # ANTI-LINK SPAM
    link_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.br', '.gg']
    link_count = sum(content.lower().count(pattern) for pattern in link_patterns)
    if link_count > 3:
        await auto_moderate_spam(message, "spam de links", f"Enviou {link_count} links em uma mensagem")
        return
    
    # Processar comandos normalmente
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
# COMANDOS DE INTERAÇÃO SOCIAL COM GIFS
# ========================================

# GIFs de anime (URLs diretas)
INTERACTION_GIFS = {
    'kiss': [
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FqBTvSNjNzeZG/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/MQVpBqASxSlFu/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/f82EqBTeCEgcU/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jR22gdcPiOLaE/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGduOG9wamdxanplenNxaG56dWQ3azdnaXlndGpoMnlndHBtYnE0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gTLfgIRwAiWOc/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/kU586ictpGb0Q/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/12VXIxKaIEarL2/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MTNoeG5oZmJxd3NxZXZ5Y3ZhNHJjM2NlaDV1dmIydGVtaDVidDdqcSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nyGFcsP0kAobm/giphy.gif'
    ],
    'hug': [
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lrr9rHuoJOE0w/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/49mdjsMrH7oze/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QFPoctlgZ5s0E/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PHZ7v9tfQu0o0/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lrr9rHuoJOE0w/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3bqtLDeiDtwhq/giphy.gif'
    ],
    'pat': [
        'https://media.tenor.com/FfEFgdPyCiYAAAAM/anime-pat.gif',
        'https://media.tenor.com/0Vj7hAId-KAAAAAC/anime-head-pat.gif',
        'https://media.tenor.com/5BIdXYCQqoMAAAAM/anime-head-pat.gif',
        'https://media.tenor.com/Q_sRzVhk52oAAAAM/anime-pat.gif',
        'https://media.tenor.com/r7RmEPHqyYwAAAAM/anime-pat.gif'
    ],
    'slap': [
        'https://media.tenor.com/BL8rTuNo_PMAAAAM/anime-slap.gif',
        'https://media.tenor.com/3Z8qVUHYZsoAAAAM/slap-anime.gif',
        'https://media.tenor.com/KNVh7dVgZhwAAAAM/anime-slap.gif',
        'https://media.tenor.com/xuMDM4tVuzAAAAAM/slap.gif',
        'https://media.tenor.com/yzHM6lBABd4AAAAM/bofetada-tapa.gif'
    ],
    'dance': [
        'https://media.tenor.com/ZdA1pYcKVe0AAAAM/anime-dance.gif',
        'https://media.tenor.com/EqQu9kXqLU0AAAAM/anime-dancing.gif',
        'https://media.tenor.com/7M-f2D_1KBAAAM/dance-anime.gif',
        'https://media.tenor.com/TpG8XnG8sHIAAAAM/anime-dance.gif',
        'https://media.tenor.com/BcvbWdzCFw0AAAAM/anime-dance.gif'
    ],
    'cry': [
        'https://media.tenor.com/8BaUXZUWnL4AAAAM/anime-cry.gif',
        'https://media.tenor.com/uNb8A2me1gUAAAAM/cry-anime.gif',
        'https://media.tenor.com/M4bsP1-8cfsAAAAM/cry-anime.gif',
        'https://media.tenor.com/YnCOBP2M3EQAAAAM/anime-crying.gif',
        'https://media.tenor.com/2X8LLmZMAnUAAAAM/anime-cry.gif'
    ]
}


# ========================================
# VIEWS COM BOTÕES DE RETRIBUIR
# ========================================

class RetribuirView(discord.ui.View):
    def __init__(self, author, target, action_type, timeout=60):
        super().__init__(timeout=timeout)
        self.author = author  # Quem enviou o comando
        self.target = target  # Quem recebeu
        self.action_type = action_type  # 'kiss', 'hug', 'pat', etc
        self.message = None
    
    @discord.ui.button(label="💝 Retribuir", style=discord.ButtonStyle.success, custom_id="retribuir_button")
    async def retribuir_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Só o alvo pode retribuir
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "❌ Só quem recebeu pode retribuir!",
                ephemeral=True
            )
            return
        
        # Desabilita o botão
        button.disabled = True
        button.label = "✅ Retribuído"
        await interaction.message.edit(view=self)
        
        # Retribui a ação
        gif = random.choice(INTERACTION_GIFS[self.action_type])
        
        if self.action_type == 'kiss':
            mensagens = [
                f'💋 **{self.target.mention}** retribuiu o beijo em **{self.author.mention}**!',
                f'😘 **{self.target.mention}** beijou **{self.author.mention}** de volta!',
                f'💕 **{self.target.mention}** correspondeu o beijo de **{self.author.mention}**!',
                f'❤️ **{self.target.mention}** não resistiu e beijou **{self.author.mention}** também!'
            ]
            titulo = '💋 Beijo Retribuído'
            cor = 0xff1493
        
        elif self.action_type == 'hug':
            mensagens = [
                f'🤗 **{self.target.mention}** retribuiu o abraço em **{self.author.mention}**!',
                f'🫂 **{self.target.mention}** abraçou **{self.author.mention}** de volta!',
                f'💛 **{self.target.mention}** correspondeu o abraço de **{self.author.mention}**!',
                f'✨ **{self.target.mention}** abraçou **{self.author.mention}** também!'
            ]
            titulo = '🤗 Abraço Retribuído'
            cor = 0xffd700
        
        elif self.action_type == 'pat':
            mensagens = [
                f'😊 **{self.target.mention}** retribuiu o carinho em **{self.author.mention}**!',
                f'🥰 **{self.target.mention}** acariciou **{self.author.mention}** de volta!',
                f'💕 **{self.target.mention}** correspondeu o carinho de **{self.author.mention}**!',
                f'✨ **{self.target.mention}** fez carinho em **{self.author.mention}** também!'
            ]
            titulo = '😊 Carinho Retribuído'
            cor = 0x87ceeb
        
        else:
            mensagens = [f'❤️ **{self.target.mention}** retribuiu a ação!']
            titulo = '💝 Retribuído'
            cor = 0xff69b4
        
        mensagem = random.choice(mensagens)
        
        embed = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cor
        )
        embed.set_image(url=gif)
        embed.set_footer(
            text=f'Retribuído por {self.target.name} • {datetime.now().strftime("%H:%M")}',
            icon_url=self.target.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def on_timeout(self):
        # Desabilita o botão quando expirar
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass

@bot.command(name='beijar')
async def beijar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para beijar!\n\n**Exemplo:**\n`.beijar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😅 Ops!',
            description='Você não pode beijar a si mesmo!\n*Tente beijar outra pessoa...*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Você não pode beijar um bot!\n*Bots não têm sentimentos...*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    # Mensagens aleatórias
    mensagens = [
        f'💋 **{ctx.author.mention}** deu um beijo em **{usuario.mention}**!',
        f'😘 **{ctx.author.mention}** beijou **{usuario.mention}** de forma romântica!',
        f'💕 **{ctx.author.mention}** roubou um beijo de **{usuario.mention}**!',
        f'😍 **{ctx.author.mention}** beijou **{usuario.mention}** apaixonadamente!',
        f'❤️ **{ctx.author.mention}** deu um beijinho em **{usuario.mention}**!',
        f'💖 **{ctx.author.mention}** surpreendeu **{usuario.mention}** com um beijo!',
        f'🌹 **{ctx.author.mention}** beijou os lábios de **{usuario.mention}**!',
        f'💝 **{ctx.author.mention}** selou os lábios de **{usuario.mention}** com um beijo!',
        f'✨ **{ctx.author.mention}** deu um beijo mágico em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** encheu **{usuario.mention}** de beijos!',
        f'💐 **{ctx.author.mention}** presenteou **{usuario.mention}** com um beijo!',
        f'🦋 **{ctx.author.mention}** deu um beijo delicado em **{usuario.mention}**!',
        f'🌺 **{ctx.author.mention}** beijou **{usuario.mention}** com paixão!'
    ]
    
    reacoes = [
        "Que momento romântico! 💕",
        "O amor está no ar! ❤️",
        "Shippo muito! 💖",
        "Que casal lindo! 😍",
        "Ahhh que fofo! 🥰",
        "Meu coração! 💗",
        "Amo esse casal! 💝",
        "Que beijo perfeito! 💋",
        "Tô morrendo de amor! 💘",
        "Casem logo! 💍"
    ]
    
    gif = random.choice(INTERACTION_GIFS['kiss'])
    mensagem = random.choice(mensagens)
    reacao = random.choice(reacoes)
    
    embed = discord.Embed(
        title='💋 Beijo Romântico',
        description=mensagem,
        color=0xff1493
    )
    embed.add_field(
        name='💕 Reação',
        value=reacao,
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'kiss', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='abracar')
async def abracar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para abraçar!\n\n**Exemplo:**\n`.abracar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='🤗 Auto-Abraço',
            description='Você se abraçou sozinho...\n*Às vezes precisamos de carinho próprio!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não podem ser abraçados!\n*Mas eles agradecem a intenção!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'🤗 **{ctx.author.mention}** deu um abraço apertado em **{usuario.mention}**!',
        f'🫂 **{ctx.author.mention}** abraçou **{usuario.mention}** carinhosamente!',
        f'💛 **{ctx.author.mention}** envolveu **{usuario.mention}** em um abraço caloroso!',
        f'🤗 **{ctx.author.mention}** deu um abraço de urso em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** abraçou **{usuario.mention}** com muito carinho!',
        f'💫 **{ctx.author.mention}** deu um abraço reconfortante em **{usuario.mention}**!',
        f'🌟 **{ctx.author.mention}** abraçou **{usuario.mention}** com todo amor!',
        f'💝 **{ctx.author.mention}** deu um abraço protetor em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** abraçou **{usuario.mention}** fortemente!',
        f'🌈 **{ctx.author.mention}** envolveu **{usuario.mention}** em um abraço acolhedor!',
        f'🦋 **{ctx.author.mention}** abraçou **{usuario.mention}** com ternura!',
        f'🌸 **{ctx.author.mention}** deu um super abraço em **{usuario.mention}**!'
    ]
    
    sentimentos = [
        "Que abraço aconchegante! 🥰",
        "Abraço que aquece o coração! ❤️",
        "Amizade verdadeira! 💛",
        "Que momento lindo! ✨",
        "Abraços curam tudo! 💫",
        "Que carinho! 🤗",
        "Energia positiva! ⚡",
        "Abraço que reconforta! 💝",
        "Que fofura! 🥺",
        "Abraço perfeito! 🌟"
    ]
    
    gif = random.choice(INTERACTION_GIFS['hug'])
    mensagem = random.choice(mensagens)
    sentimento = random.choice(sentimentos)
    
    embed = discord.Embed(
        title='🤗 Abraço Carinhoso',
        description=mensagem,
        color=0xffd700
    )
    embed.add_field(
        name='💛 Sentimento',
        value=sentimento,
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'hug', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='acariciar')
async def acariciar_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para acariciar!\n\n**Exemplo:**\n`.acariciar @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😌 Auto-Carinho',
            description='Você faz carinho em si mesmo...\n*Self-care é importante!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não sentem carinhos!\n*Mas obrigado pela gentileza!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'😊 **{ctx.author.mention}** acariciou a cabeça de **{usuario.mention}**!',
        f'🥰 **{ctx.author.mention}** fez um carinho em **{usuario.mention}**!',
        f'✨ **{ctx.author.mention}** deu head pat em **{usuario.mention}**!',
        f'💕 **{ctx.author.mention}** acariciou **{usuario.mention}** gentilmente!',
        f'🌸 **{ctx.author.mention}** fez cafuné em **{usuario.mention}**!',
        f'😌 **{ctx.author.mention}** acariciou **{usuario.mention}** com carinho!',
        f'🎀 **{ctx.author.mention}** passou a mão na cabeça de **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** deu um carinho delicado em **{usuario.mention}**!',
        f'🌺 **{ctx.author.mention}** acariciou **{usuario.mention}** suavemente!',
        f'🦋 **{ctx.author.mention}** fez um carinho relaxante em **{usuario.mention}**!',
        f'🌷 **{ctx.author.mention}** mimou **{usuario.mention}** com carinhos!',
        f'🌼 **{ctx.author.mention}** deu head pats em **{usuario.mention}**!'
    ]
    
    efeitos = [
        "Que relaxante! 😌",
        "Carinho gostoso! 🥰",
        "Tão fofo! 💕",
        "Que delícia! ✨",
        "Carinho que acalma! 💫",
        "Que mimo! 🌸",
        "Terapêutico! 💆",
        "Carinho perfeito! 🎀",
        "Que gentileza! 🌺",
        "Adorei! 😊"
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    efeito = random.choice(efeitos)
    
    embed = discord.Embed(
        title='😊 Carinho Gentil',
        description=mensagem,
        color=0x87ceeb
    )
    embed.add_field(
        name='💕 Efeito',
        value=efeito,
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'pat', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

@bot.command(name='tapa')
async def tapa_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para dar um tapa!\n\n**Exemplo:**\n`.tapa @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='🤕 Auto-Tapa',
            description='Você se deu um tapa... Por quê?!\n*Isso deve ter doído!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Não bata em bots!\n*Eles são inocentes!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'👋 **{ctx.author.mention}** deu um tapa na cara de **{usuario.mention}**!',
        f'💥 **{ctx.author.mention}** acertou um tapão monumental em **{usuario.mention}**!',
        f'✋ **{ctx.author.mention}** esfregou a mão na cara de **{usuario.mention}**!',
        f'😤 **{ctx.author.mention}** deu uma bela palmada em **{usuario.mention}**!',
        f'🔥 **{ctx.author.mention}** mandou um tapa épico em **{usuario.mention}**!',
        f'💢 **{ctx.author.mention}** não perdoou e tapou **{usuario.mention}**!',
        f'⚡ **{ctx.author.mention}** deu um tapa que ecoou no servidor em **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** acertou um super tapa em **{usuario.mention}**!',
        f'🌪️ **{ctx.author.mention}** mandou ver na cara de **{usuario.mention}**!',
        f'💪 **{ctx.author.mention}** mostrou quem manda com um tapa em **{usuario.mention}**!'
    ]
    
    reacoes = [
        "Isso deve ter doído!",
        "Que tapa sonoro!",
        "Ouvi o barulho daqui!",
        "Eita! Sem dó nem piedade!",
        "RIP a dignidade...",
        "Marcou até!",
        "Acho que acordou os vizinhos!",
        "Alguém chame a ambulância!",
        "Voou até!",
        "Que pancada!"
    ]
    
    gif = random.choice(INTERACTION_GIFS['slap'])
    mensagem = random.choice(mensagens)
    reacao = random.choice(reacoes)
    
    embed = discord.Embed(
        title='👋 Tapa Épico',
        description=mensagem,
        color=0xff4444
    )
    embed.add_field(
        name='💥 Reação',
        value=reacao,
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='dancar')
async def dancar_command(ctx, usuario: discord.Member = None):
    gif = random.choice(INTERACTION_GIFS['dance'])
    
    if usuario:
        if usuario.id == ctx.author.id:
            embed = discord.Embed(
                title='💃 Dança Solo',
                description=f'**{ctx.author.mention}** está dançando sozinho como se ninguém estivesse olhando!\n*Que show!*',
                color=0x9b59b6
            )
        elif usuario.bot:
            embed = discord.Embed(
                title='🤖 Erro',
                description='Bots não dançam!\n*Mas seria legal se dançassem...*',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return
        else:
            mensagens = [
                f'💃 **{ctx.author.mention}** está dançando com **{usuario.mention}**!',
                f'🕺 **{ctx.author.mention}** e **{usuario.mention}** estão arrasando na pista!',
                f'✨ **{ctx.author.mention}** chamou **{usuario.mention}** para dançar!',
                f'🎵 **{ctx.author.mention}** e **{usuario.mention}** dançam sincronizados!',
                f'🌟 Que dupla incrível! **{ctx.author.mention}** e **{usuario.mention}** mandando ver!',
                f'💫 **{ctx.author.mention}** rodou **{usuario.mention}** na pista de dança!'
            ]
            mensagem = random.choice(mensagens)
            embed = discord.Embed(
                title='💃 Dança em Dupla',
                description=mensagem,
                color=0x9b59b6
            )
    else:
        mensagens_solo = [
            f'💃 **{ctx.author.mention}** está dançando sozinho!',
            f'🕺 **{ctx.author.mention}** mandou ver nos passos!',
            f'✨ **{ctx.author.mention}** está arrasando na pista!',
            f'🎵 **{ctx.author.mention}** dançando como se ninguém estivesse olhando!',
            f'🌟 **{ctx.author.mention}** está fazendo um show solo!',
            f'💫 Que performance! **{ctx.author.mention}** dançando demais!',
            f'🎪 **{ctx.author.mention}** está quebrando tudo na pista!',
            f'🔥 **{ctx.author.mention}** está dançando pra caramba!',
            f'⚡ **{ctx.author.mention}** mostrando seus melhores passos!',
            f'🌈 **{ctx.author.mention}** está se divertindo muito!'
        ]
        
        comentarios = [
            "Que energia incrível!",
            "Arrasou nos passos!",
            "Tá pegando fogo!",
            "Show de performance!",
            "Que talento!",
            "A pista é sua!",
            "Que ritmo maravilhoso!",
            "Está no flow!",
            "Mandou muito bem!",
            "Isso é arte!"
        ]
        
        mensagem = random.choice(mensagens_solo)
        comentario = random.choice(comentarios)
        
        embed = discord.Embed(
            title='💃 Dança Solo',
            description=mensagem,
            color=0x9b59b6
        )
        embed.add_field(
            name='🎭 Performance',
            value=comentario,
            inline=False
        )
    
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='chorar')
async def chorar_command(ctx):
    mensagens = [
        f'😭 **{ctx.author.mention}** está chorando muito...',
        f'💧 **{ctx.author.mention}** não aguenta mais e chora...',
        f'😢 As lágrimas de **{ctx.author.mention}** não param de cair...',
        f'😿 **{ctx.author.mention}** está chorando copiosamente...',
        f'💔 **{ctx.author.mention}** chora de tristeza...',
        f'🥺 **{ctx.author.mention}** soltou as lágrimas...',
        f'😭 **{ctx.author.mention}** está em prantos...',
        f'💧 **{ctx.author.mention}** chora sem parar...',
        f'😢 **{ctx.author.mention}** está muito emocionado...',
        f'🌧️ **{ctx.author.mention}** derramou lágrimas...'
    ]
    
    motivos = [
        "Parece que está triste hoje...",
        "Algo não está bem...",
        "O dia está difícil...",
        "Está precisando de apoio...",
        "Momento de desabafo...",
        "Deixa chorar, faz bem...",
        "Às vezes precisamos extravasar...",
        "Um abraço resolve...",
        "Console essa pessoa!",
        "Está precisando de carinho..."
    ]
    
    gif = random.choice(INTERACTION_GIFS['cry'])
    mensagem = random.choice(mensagens)
    motivo = random.choice(motivos)
    
    embed = discord.Embed(
        title='😭 Momento Triste',
        description=mensagem,
        color=0x5865f2
    )
    embed.add_field(
        name='💭 Situação',
        value=motivo,
        inline=False
    )
    embed.add_field(
        name='💝 Apoio',
        value='Envie um abraço ou carinho para essa pessoa! Use `.abracar` ou `.acariciar`',
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)


@bot.command(name='ship')
async def ship_command(ctx, user1: discord.Member = None, user2: discord.Member = None):
    if not user1 or not user2:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar 2 pessoas!\n\n**Exemplo:**\n`.ship @user1 @user2`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if user1.bot or user2.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Não dá pra shipar bots!\n*Eles não têm sentimentos românticos!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if user1.id == user2.id:
        embed = discord.Embed(
            title='😅 Narcisismo Detected',
            description=f'**{user1.mention}** não pode ser shipado consigo mesmo!\n*Mas o amor próprio é importante!* ❤️',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    # Calcula porcentagem de ship (baseado em IDs para ser consistente)
    ship_value = (user1.id + user2.id) % 101
    
    # Nome do ship (junção dos nomes)
    name1 = user1.display_name[:len(user1.display_name)//2]
    name2 = user2.display_name[len(user2.display_name)//2:]
    ship_name = f"{name1}{name2}"
    
    # Barra de progresso visual
    filled = '❤️' * (ship_value // 10)
    empty = '🖤' * (10 - ship_value // 10)
    bar = filled + empty
    
    # Mensagem baseada na porcentagem com mais variedade
    if ship_value >= 90:
        emoji = "💕"
        message = "PERFEIÇÃO ABSOLUTA! Casal do ano! Casem logo!"
        cor = 0xff1493  # Pink forte
    elif ship_value >= 75:
        emoji = "💖"
        message = "Extremamente compatíveis! Isso vai dar certo!"
        cor = 0xff69b4  # Pink médio
    elif ship_value >= 60:
        emoji = "💗"
        message = "Muito compatíveis! Vale a pena tentar!"
        cor = 0xffc0cb  # Pink claro
    elif ship_value >= 45:
        emoji = "💛"
        message = "Pode dar certo! Precisam se conhecer melhor!"
        cor = 0xffd700  # Dourado
    elif ship_value >= 30:
        emoji = "💙"
        message = "Quem sabe com um pouco de esforço..."
        cor = 0x87ceeb  # Azul claro
    elif ship_value >= 15:
        emoji = "💚"
        message = "Improvável... Mas milagres acontecem!"
        cor = 0x90ee90  # Verde claro
    else:
        emoji = "💔"
        message = "Péssimo! Melhor serem apenas amigos..."
        cor = 0x808080  # Cinza
    
    embed = discord.Embed(
        title=f'💘 SHIPAGEM: {ship_name.upper()}',
        description=f'**{user1.display_name}** {emoji} **{user2.display_name}**',
        color=cor
    )
    
    embed.add_field(
        name='📊 Compatibilidade',
        value=f'{bar}\n**{ship_value}%**',
        inline=False
    )
    
    embed.add_field(
        name='💬 Resultado',
        value=message,
        inline=False
    )
    
    # Adiciona "curiosidades" aleatórias
    curiosidades = [
        "🎭 Opostos se atraem!",
        "🌟 A química é evidente!",
        "🔥 Que casal quente!",
        "❄️ Clima de frieza...",
        "⚡ A energia entre vocês é incrível!",
        "🌈 Amor colorido!",
        "💫 Conexão cósmica!",
        "🎪 Que palhaçada seria esse relacionamento!",
        "🎨 Vocês se complementam perfeitamente!",
        "🎵 Em harmonia total!"
    ]
    
    if ship_value >= 50:
        curiosidade = random.choice([c for c in curiosidades if not "frieza" in c.lower() and not "palhaçada" in c.lower()])
    else:
        curiosidade = random.choice(curiosidades)
    
    embed.add_field(
        name='✨ Análise',
        value=curiosidade,
        inline=False
    )
    
    embed.set_footer(
        text=f'Ship feito por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Enviar embed (sem imagem)
    await ctx.reply(embed=embed)

# ========================================
# COMANDOS DE ZOEIRA PESADA
# ========================================

@bot.command(name='vaitomarnocu')
async def vaitomarnocu_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Menciona alguém pra xingar, oras!')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('🤡 Quer xingar você mesmo? Procure ajuda profissional!')
        return
    
    if usuario.bot:
        await ctx.reply('🤖 Deixa os bots em paz, eles só fazem o trabalho deles!')
        return
    
    xingamentos = [
        f'🖕 **{ctx.author.mention}** mandou **{usuario.mention}** tomar no cu!',
        f'💢 **{ctx.author.mention}** disse: **{usuario.mention}**, vai se fuder!',
        f'😤 **{ctx.author.mention}** falou pra **{usuario.mention}** ir pra pqp!',
        f'🔥 **{ctx.author.mention}** mandou **{usuario.mention}** à merda!',
        f'💀 **{ctx.author.mention}** disse: **{usuario.mention}**, vai catar coquinho!',
        f'⚡ **{ctx.author.mention}** mandou **{usuario.mention}** se foder!',
        f'👊 **{ctx.author.mention}** disse: **{usuario.mention}**, vai tomar no olho do seu cu!',
        f'💥 **{ctx.author.mention}** mandou **{usuario.mention}** pra casa do caralho!',
        f'🌪️ **{ctx.author.mention}** falou: **{usuario.mention}**, vai se lascar!',
        f'🔨 **{ctx.author.mention}** disse: **{usuario.mention}**, vai pra puta que pariu!',
        f'💣 **{ctx.author.mention}** mandou **{usuario.mention}** pra aquele lugar!',
        f'🎯 **{ctx.author.mention}** disse: **{usuario.mention}**, vai mamar!',
        f'⛈️ **{ctx.author.mention}** falou: **{usuario.mention}**, vai pro inferno!',
        f'🌋 **{ctx.author.mention}** mandou **{usuario.mention}** tomar no centro do cu!',
        f'💨 **{ctx.author.mention}** disse: **{usuario.mention}**, vai chupar um canavial!',
        f'🗡️ **{ctx.author.mention}** mandou **{usuario.mention}** pra casa do caralho de asas!',
        f'⚔️ **{ctx.author.mention}** disse: **{usuario.mention}**, vai pastar!',
        f'🔪 **{ctx.author.mention}** falou: **{usuario.mention}**, vai se ferrar na esquina!',
        f'💢 **{ctx.author.mention}** mandou **{usuario.mention}** enfiar o dedo no cu e rodar!',
        f'🎭 **{ctx.author.mention}** disse: **{usuario.mention}**, vai pro caralho que te pariu!'
    ]
    
    mensagem = random.choice(xingamentos)
    
    embed = discord.Embed(
        title='💢 Xingamento Pesado',
        description=mensagem,
        color=0xff0000
    )
    embed.set_footer(
        text=f'É zoeira! • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='filhodaputa')
async def filhodaputa_command(ctx, usuario: discord.Member = None):
    if not usuario:
        await ctx.reply('❌ Menciona alguém pra xingar, oras!')
        return
    
    if usuario.id == ctx.author.id:
        await ctx.reply('🤡 Você é filho da puta? Não precisa confirmar!')
        return
    
    if usuario.bot:
        await ctx.reply('🤖 Bots não têm mãe, deixa eles quietos!')
        return
    
    xingamentos = [
        f'🖕 **{ctx.author.mention}** chamou **{usuario.mention}** de filho da puta!',
        f'💀 **{ctx.author.mention}** disse: **{usuario.mention}** é um fdp mesmo!',
        f'🔥 **{ctx.author.mention}** confirmou: **{usuario.mention}** é filho duma puta!',
        f'💢 **{ctx.author.mention}** falou: **{usuario.mention}**, seu filho da mãe!',
        f'⚡ **{ctx.author.mention}** disse: **{usuario.mention}** é um desgraçado!',
        f'👊 **{ctx.author.mention}** chamou **{usuario.mention}** de arrombado!',
        f'💥 **{ctx.author.mention}** falou: **{usuario.mention}** é um babaca do caralho!',
        f'🌪️ **{ctx.author.mention}** disse: **{usuario.mention}** é um merda!',
        f'🔨 **{ctx.author.mention}** chamou **{usuario.mention}** de corno manso!',
        f'💣 **{ctx.author.mention}** falou: **{usuario.mention}** é um bosta!',
        f'🎯 **{ctx.author.mention}** disse: **{usuario.mention}** é um lixo humano!',
        f'⛈️ **{ctx.author.mention}** chamou **{usuario.mention}** de pilantra!',
        f'🌋 **{ctx.author.mention}** falou: **{usuario.mention}** é um verme!',
        f'💨 **{ctx.author.mention}** disse: **{usuario.mention}** é um cuzão!',
        f'🗡️ **{ctx.author.mention}** chamou **{usuario.mention}** de energúmeno!',
        f'⚔️ **{ctx.author.mention}** falou: **{usuario.mention}** é um retardado!',
        f'🔪 **{ctx.author.mention}** disse: **{usuario.mention}** é um imbecil!',
        f'🎭 **{ctx.author.mention}** chamou **{usuario.mention}** de pau no cu!',
        f'🏴 **{ctx.author.mention}** falou: **{usuario.mention}** é um fracassado!',
        f'⚠️ **{ctx.author.mention}** disse: **{usuario.mention}** é um escroto!'
    ]
    
    gifs = [
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/44Eq3Ab5LPYn6/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yV5xcSTmtVPBS/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l4Fsly71gEOtGvLQA/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FNMXxCshJxel7cRYuj/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ImWifslsGZjrSyxyjM/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/I7p8K5EY9w9dC/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/KzGCAlMiK6hQQ/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/BXHtzkBTqd9dAemgCL/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmxkejQxbnU2OGk3NGcwOHRiNGFqZHRlZHE2enAzc2xib3VpMTg2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/U7P2vnWfPkIQ8/giphy.gif'
    ]
    
    mensagem = random.choice(xingamentos)
    gif = random.choice(gifs)
    
    embed = discord.Embed(
        title='🔥 Xingamento Destruidor',
        description=mensagem,
        color=0xff0000
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'É brincadeira, relaxa! • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.reply(embed=embed)

@bot.command(name='cafune')
async def cafune_command(ctx, usuario: discord.Member = None):
    if not usuario:
        embed = discord.Embed(
            title='❌ Erro no Comando',
            description='Você precisa mencionar alguém para fazer cafuné!\n\n**Exemplo:**\n`.cafune @user`',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.id == ctx.author.id:
        embed = discord.Embed(
            title='😌 Auto-Cafuné',
            description='Você faz cafuné em si mesmo... Relaxante!\n*Self-care extremo!*',
            color=0xffa500
        )
        await ctx.reply(embed=embed)
        return
    
    if usuario.bot:
        embed = discord.Embed(
            title='🤖 Erro',
            description='Bots não têm cabelo para fazer cafuné!\n*Mas agradecem pela intenção!*',
            color=0xff0000
        )
        await ctx.reply(embed=embed)
        return
    
    mensagens = [
        f'😌 **{ctx.author.mention}** está fazendo cafuné em **{usuario.mention}**!',
        f'💆 **{ctx.author.mention}** acaricia a cabeça de **{usuario.mention}** suavemente!',
        f'✨ **{ctx.author.mention}** faz um cafuné relaxante em **{usuario.mention}**!',
        f'🌸 **{ctx.author.mention}** passa a mão no cabelo de **{usuario.mention}**!',
        f'💤 **{ctx.author.mention}** está fazendo **{usuario.mention}** relaxar com cafuné!',
        f'🥰 **{ctx.author.mention}** dá um cafuné carinhoso em **{usuario.mention}**!',
        f'🎀 **{ctx.author.mention}** faz cafuné gostoso em **{usuario.mention}**!',
        f'💫 **{ctx.author.mention}** está mimando **{usuario.mention}** com cafuné!',
        f'🌺 **{ctx.author.mention}** dá um cafuné delicioso em **{usuario.mention}**!',
        f'🦋 **{ctx.author.mention}** faz cafuné que dá sono em **{usuario.mention}**!',
        f'🌷 **{ctx.author.mention}** está fazendo **{usuario.mention}** dormir com cafuné!',
        f'🌼 **{ctx.author.mention}** dá o melhor cafuné em **{usuario.mention}**!'
    ]
    
    beneficios = [
        "Que paz! 😌",
        "Puro relaxamento! 💆",
        "Quase dormindo... 💤",
        "Que delícia! 🥰",
        "Terapêutico! ✨",
        "Que carinho gostoso! 💕",
        "Relaxa demais! 🌸",
        "Melhor sensação! 💫",
        "Tão bom! 🎀",
        "Cafuné perfeito! 🌺"
    ]
    
    gif = random.choice(INTERACTION_GIFS['pat'])
    mensagem = random.choice(mensagens)
    beneficio = random.choice(beneficios)
    
    embed = discord.Embed(
        title='😌 Cafuné Relaxante',
        description=mensagem,
        color=0xffc0cb
    )
    embed.add_field(
        name='💆 Benefício',
        value=beneficio,
        inline=False
    )
    embed.add_field(
        name='✨ Momento',
        value='Momento de paz e relaxamento...',
        inline=False
    )
    embed.set_image(url=gif)
    embed.set_footer(
        text=f'Comando usado por {ctx.author.name} • {datetime.now().strftime("%H:%M")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Criar view com botão de retribuir
    view = RetribuirView(ctx.author, usuario, 'pat', timeout=60)
    message = await ctx.reply(embed=embed, view=view)
    view.message = message

# ========================================
# COMANDOS DE XP/RANK (ESTILO LORITTA)
# ========================================

@bot.command(name='rank')
async def rank_command(ctx, user: discord.Member = None):
    """Ver rank com card visual tipo Loritta"""
    user = user or ctx.author
    
    try:
        await ctx.defer() if hasattr(ctx, 'defer') else None
        
        # Busca dados do usuário
        data = get_user_xp(user.id, ctx.guild.id)
        level = data['level']
        xp = data['xp']
        messages = data['messages']
        xp_needed = calculate_xp_for_level(level + 1)
        rank_position = get_user_rank(user.id, ctx.guild.id)
        
        # Gera rank card via Vacefron API com background customizado CAOS
        params = {
            'username': user.name,
            'avatar': str(user.display_avatar.url),
            'level': level,
            'rank': rank_position,
            'currentxp': xp,
            'nextlevelxp': xp_needed,
            'previouslevelxp': 0,
            'custombg': 'https://i.ibb.co/BVX3K2Y2/1.png',  # Background customizado laranja CAOS
            'xpcolor': 'FF6600'
        }
        
        url = f"https://vacefron.nl/api/rankcard?{urlencode(params)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    file = discord.File(fp=BytesIO(image_bytes), filename='rank.png')
                else:
                    await ctx.reply("❌ Erro ao gerar rank card!")
                    return
        
        # Embed com info extra
        embed = discord.Embed(
            title=f"📊 Rank de {user.name}",
            color=0xff6600
        )
        embed.add_field(name="📨 Mensagens", value=f"`{messages:,}`", inline=True)
        embed.add_field(name="🏆 Posição", value=f"`#{rank_position}`", inline=True)
        embed.add_field(name="📈 Próximo Nível", value=f"`{xp_needed - xp:,} XP`", inline=True)
        
        # Verificar se tem cargo por nível
        conn = sqlite3.connect('xp_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT role_id FROM level_roles WHERE guild_id = ? AND level = ?', 
                     (str(ctx.guild.id), level))
        role_result = cursor.fetchone()
        conn.close()
        
        if role_result:
            role = ctx.guild.get_role(int(role_result[0]))
            if role:
                embed.add_field(name="🎖️ Cargo Atual", value=role.mention, inline=False)
        
        embed.set_image(url="attachment://rank.png")
        embed.set_footer(text="Sistema de XP tipo Loritta • CAOS Hub")
        
        await ctx.reply(embed=embed, file=file)
    except Exception as e:
        print(f'❌ Erro no comando rank: {e}')
        await ctx.reply(f"❌ Erro ao buscar rank: {e}")

@bot.command(name='rankxp', aliases=['leaderboard', 'lb', 'top'])
async def rankxp_command(ctx):
    """Ver top 10 usuários do servidor com visual estilo Loritta"""
    try:
        top_users = get_leaderboard(ctx.guild.id, 10)
        
        if not top_users:
            await ctx.reply("❌ Ainda não há usuários no ranking!")
            return
        
        # Cria descrição elaborada com visual de ranking
        description_lines = []
        medals = ['🥇', '🥈', '🥉']
        
        for i, (user_id, xp, level, messages) in enumerate(top_users, 1):
            user = ctx.guild.get_member(int(user_id))
            if user:
                medal = medals[i-1] if i <= 3 else f"**`#{i:02d}`**"
                
                # Barra de progresso visual
                xp_bar_length = min(int((xp / max(top_users[0][1], 1)) * 10), 10)
                xp_bar = "█" * xp_bar_length + "░" * (10 - xp_bar_length)
                
                description_lines.append(
                    f"{medal} **{user.name}**\n"
                    f"└ `Lv.{level:02d}` • {xp_bar} • `{xp:,} XP` • `{messages:,} msgs`\n"
                )
        
        embed = discord.Embed(
            title=f"🏆 RANKING DE XP • {ctx.guild.name.upper()}",
            description="\n".join(description_lines) + f"\n\n**📊 Total de membros no ranking:** `{len(top_users)}`",
            color=0xff6600
        )
        
        # Adiciona avatar do #1 como thumbnail
        if top_users:
            first_user = ctx.guild.get_member(int(top_users[0][0]))
            if first_user:
                embed.set_thumbnail(url=first_user.display_avatar.url)
        
        # Banner do servidor como imagem principal
        if ctx.guild.banner:
            embed.set_image(url=ctx.guild.banner.url)
        elif ctx.guild.icon:
            embed.set_image(url=ctx.guild.icon.url)
        else:
            # Usa imagem do CAOS como fallback
            embed.set_image(url="https://i.ibb.co/BVX3K2Y2/1.png")
        
        embed.set_footer(
            text="🔥 Sistema de XP tipo Loritta • Use .rank pra ver seu card individual",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f'❌ Erro no rankxp: {e}')
        await ctx.reply(f"❌ Erro ao buscar ranking: {e}")

@bot.command(name='setxp')
@commands.has_permissions(administrator=True)
async def setxp_command(ctx, user: discord.Member, xp: int):
    """Define XP de um usuário (Admin)"""
    try:
        conn = sqlite3.connect('xp_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_xp (user_id, guild_id, xp, level, messages, last_xp_time)
            VALUES (?, ?, ?, 0, 0, ?)
        ''', (str(user.id), str(ctx.guild.id), xp, time.time()))
        conn.commit()
        conn.close()
        
        await ctx.reply(f"✅ XP de {user.mention} definido para **{xp:,} XP**!")
    except Exception as e:
        await ctx.reply(f"❌ Erro: {e}")

@setxp_command.error
async def setxp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")

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

# COMANDO .toggletickets REMOVIDO - USE O DASHBOARD
# Acesse: https://caosbot-discord.onrender.com/dashboard

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

# IDs dos cargos de STAFF (hierarquia do maior pro menor)
FOUNDER_ROLE_ID = 1365636960651051069    # [FND] Founder
SUBDONO_ROLE_ID = 1365636456386789437    # [SDN] Sub Dono
ADMIN_ROLE_ID = 1365633918593794079      # [ADM] Administrador
STAFF_ROLE_ID = 1365634226254254150      # [STF] Staff
MOD_ROLE_ID = 1365633102973763595        # [MOD] Moderador
SUBMOD_ROLE_ID = 1365631940434333748     # [SBM] Sub Moderador

# IDs dos cargos ADV
ADV_CARGO_1_ID = 1365861145738477598  # ADV 1
ADV_CARGO_2_ID = 1365861187392241714  # ADV 2
ADV_CARGO_3_ID = 1365861225900277832  # ADV 3

# ID do canal de logs
LOG_CHANNEL_ID = 1417638740435800186

# Hierarquia de cargos (maior número = mais poder)
ROLE_HIERARCHY = {
    FOUNDER_ROLE_ID: 6,  # Founder
    SUBDONO_ROLE_ID: 5,  # Sub Dono
    ADMIN_ROLE_ID: 4,    # Administrador
    STAFF_ROLE_ID: 3,    # Staff
    MOD_ROLE_ID: 2,      # Moderador
    SUBMOD_ROLE_ID: 1    # Sub Moderador
}

def get_highest_staff_role(member):
    """Retorna o cargo de staff mais alto do membro e seu nível de hierarquia"""
    highest_level = 0
    highest_role = None
    
    for role in member.roles:
        if role.id in ROLE_HIERARCHY:
            level = ROLE_HIERARCHY[role.id]
            if level > highest_level:
                highest_level = level
                highest_role = role
    
    return highest_role, highest_level

def can_moderate(moderator, target):
    """Verifica se o moderador pode punir o alvo baseado na hierarquia"""
    mod_role, mod_level = get_highest_staff_role(moderator)
    target_role, target_level = get_highest_staff_role(target)
    
    # Se o alvo não tem cargo de staff, pode punir
    if target_level == 0:
        return True, None
    
    # Se o moderador tem cargo maior, pode punir
    if mod_level > target_level:
        return True, None
    
    # Se tem o mesmo nível ou menor, não pode
    if mod_level <= target_level:
        return False, target_role
    
    return False, None

# Arquivo para salvar dados das advertências
WARNINGS_FILE = "warnings_data.json"

# Dicionário para rastrear advertências dos usuários com detalhes completos
user_warnings = {}
user_warnings_details = {}  # Detalhes das advertências: motivo, moderador, timestamp

# Sistema de nicknames automáticos por cargo (configurado com IDs reais)
CARGO_PREFIXES = {
    # Cargos de moderação do servidor (IDs fornecidos pelo usuário)
    1365636960651051069: "[FND]",  # Founder
    1365636456386789437: "[SDN]",  # Sub Dono
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

# Estado do sistema (DESATIVADO por padrão - aguarda dashboard)
welcome_config = {
    'welcome_enabled': False,  # ❌ Aguardando dashboard
    'goodbye_enabled': False,  # ❌ Aguardando dashboard
    'autorole_enabled': False,  # ❌ Aguardando dashboard
    'tickets_enabled': False,  # ❌ Aguardando dashboard
    'status_message_id': None
}

# ===============================
# Helpers de normalização de toggles
# ===============================
def to_bool(value):
    """Converte qualquer valor comum em boolean consistente."""
    try:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            v = value.strip().lower()
            return v in ("1", "true", "on", "yes", "y", "enabled")
    except Exception:
        pass
    return False

def normalize_config(cfg: dict) -> dict:
    """Garante que as chaves de toggle sejam sempre booleanas."""
    for key in ("welcome_enabled", "goodbye_enabled", "autorole_enabled", "tickets_enabled"):
        if key in cfg:
            cfg[key] = to_bool(cfg.get(key))
        else:
            cfg[key] = False
    return cfg

def is_on(key: str) -> bool:
    """Retorna o valor booleano normalizado do toggle atual em memória."""
    return to_bool(welcome_config.get(key))

def save_welcome_config():
    """Salva configurações do sistema de boas-vindas"""
    try:
        with open(WELCOME_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(welcome_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configurações de boas-vindas salvas")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações de boas-vindas: {e}")

def load_welcome_config():
    """Carrega configurações do sistema de boas-vindas DO ARQUIVO LOCAL"""
    global welcome_config
    try:
        # DESATIVADO: Não tenta conectar ao dashboard externo (causa loop)
        # Usa apenas arquivo local para evitar problemas de inicialização
        
        # Ler do arquivo local
        if os.path.exists(WELCOME_CONFIG_FILE):
            with open(WELCOME_CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                welcome_config.update(normalize_config(loaded_config))
            print(f"✅ Configurações carregadas do arquivo local")
            print(f"   Welcome: {is_on('welcome_enabled')}")
            print(f"   Goodbye: {is_on('goodbye_enabled')}")
            print(f"   Autorole: {is_on('autorole_enabled')}")
            print(f"   Tickets: {is_on('tickets_enabled')}")
        else:
            # Se não existe arquivo, cria um padrão
            print("📝 Arquivo de configuração não encontrado, criando padrão...")
            welcome_config.update({
                'welcome_enabled': True,
                'goodbye_enabled': True,
                'autorole_enabled': False,
                'tickets_enabled': True
            })
            save_welcome_config()
            print(f"✅ Configurações padrão criadas")
            print(f"   Welcome: {is_on('welcome_enabled')}")
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        print("   Mantendo tudo DESATIVADO por segurança")

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

# Sistema de contadores de tickets por categoria
ticket_counters = defaultdict(int)  # Contador incremental por categoria

# ========================================
# SISTEMA ANTI-RAID AVANÇADO
# ========================================
raid_detection = {
    'enabled': True,
    'in_raid_mode': False,
    'raid_start_time': None,
    'recent_joins': deque(maxlen=20),  # Últimas 20 entradas
    'recent_messages': deque(maxlen=100),  # Últimas 100 mensagens
    'suspicious_users': set(),  # Usuários suspeitos
    'auto_banned': set(),  # IDs de usuários banidos automaticamente
}

# Configurações do anti-raid
RAID_CONFIG = {
    'join_threshold': 10,  # Número de entradas para ativar modo raid
    'join_timeframe': 60,  # Em quantos segundos (10 entradas em 60s = raid)
    'message_threshold': 15,  # Mensagens no servidor (DIMINUÍDO PARA TESTAR - era 50)
    'message_timeframe': 10,  # Janela de tempo para contar mensagens
    'account_age_min': 7,  # Dias mínimos de conta (contas novas são suspeitas)
    'lockdown_duration': 300,  # Segundos em modo raid (5 minutos)
    'slowmode_duration': 5,  # Segundos de slowmode durante raid
}

async def check_raid_pattern(guild):
    """Verifica se há padrão de raid (entradas massivas)"""
    if not raid_detection['enabled']:
        return False
    
    current_time = time.time()
    recent_joins = raid_detection['recent_joins']
    
    # Limpar entradas antigas
    while recent_joins and current_time - recent_joins[0] > RAID_CONFIG['join_timeframe']:
        recent_joins.popleft()
    
    # Se tiver muitas entradas recentes
    if len(recent_joins) >= RAID_CONFIG['join_threshold']:
        return True
    
    return False

async def check_message_flood(guild):
    """Verifica se há flood de mensagens no servidor"""
    current_time = time.time()
    recent_messages = raid_detection['recent_messages']
    
    # Limpar mensagens antigas
    while recent_messages and current_time - recent_messages[0] > RAID_CONFIG['message_timeframe']:
        recent_messages.popleft()
    
    # Se tiver muitas mensagens em pouco tempo
    messages_per_second = len(recent_messages) / RAID_CONFIG['message_timeframe']
    if messages_per_second >= (RAID_CONFIG['message_threshold'] / RAID_CONFIG['message_timeframe']):
        return True
    
    return False

async def activate_raid_mode(guild):
    """Ativa modo anti-raid no servidor"""
    if raid_detection['in_raid_mode']:
        return  # Já está em modo raid
    
    raid_detection['in_raid_mode'] = True
    raid_detection['raid_start_time'] = time.time()
    
    print(f"🚨 MODO ANTI-RAID ATIVADO em {guild.name}")
    
    # Canal de logs
    log_channel = guild.get_channel(1315107491453444137)  # Canal de logs
    
    if log_channel:
        embed = discord.Embed(
            title="🚨 MODO ANTI-RAID ATIVADO",
            description="**Raid detectado! Medidas de proteção ativadas.**",
            color=0xFF0000,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="🛡️ Proteções Ativas",
            value=(
                "✅ Slowmode (5s) em todos os canais\n"
                "✅ Auto-ban de contas novas (<7 dias)\n"
                "✅ Bloqueio de spam intensificado\n"
                "✅ Monitoramento ativo"
            ),
            inline=False
        )
        embed.add_field(
            name="⏱️ Duração",
            value=f"{RAID_CONFIG['lockdown_duration'] // 60} minutos (automático)",
            inline=False
        )
        embed.set_footer(text="Sistema Anti-Raid • Caos Hub")
        await log_channel.send("@everyone", embed=embed)
    
    # Aplicar slowmode em canais de texto
    for channel in guild.text_channels:
        try:
            if channel.slowmode_delay == 0:  # Só aplicar se não tiver slowmode
                await channel.edit(slowmode_delay=RAID_CONFIG['slowmode_duration'])
        except:
            pass
    
    # Agendar desativação automática
    await asyncio.sleep(RAID_CONFIG['lockdown_duration'])
    await deactivate_raid_mode(guild)

async def deactivate_raid_mode(guild):
    """Desativa modo anti-raid"""
    if not raid_detection['in_raid_mode']:
        return
    
    raid_detection['in_raid_mode'] = False
    raid_detection['raid_start_time'] = None
    raid_detection['suspicious_users'].clear()
    
    print(f"✅ MODO ANTI-RAID DESATIVADO em {guild.name}")
    
    # Canal de logs
    log_channel = guild.get_channel(1315107491453444137)
    
    if log_channel:
        embed = discord.Embed(
            title="✅ MODO ANTI-RAID DESATIVADO",
            description="Servidor voltou ao normal.",
            color=0x00FF00,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Sistema Anti-Raid • Caos Hub")
        await log_channel.send(embed=embed)
    
    # Remover slowmode
    for channel in guild.text_channels:
        try:
            if channel.slowmode_delay == RAID_CONFIG['slowmode_duration']:
                await channel.edit(slowmode_delay=0)
        except:
            pass

async def check_suspicious_user(member):
    """Verifica se um usuário é suspeito (conta nova, bot, etc)"""
    # Verificar idade da conta
    account_age = (discord.utils.utcnow() - member.created_at).days
    
    # Conta muito nova
    if account_age < RAID_CONFIG['account_age_min']:
        return True, f"Conta criada há {account_age} dias"
    
    # Avatar padrão + conta nova
    if member.avatar is None and account_age < 30:
        return True, "Sem avatar + conta nova"
    
    # Nome suspeito (muitos números)
    if sum(c.isdigit() for c in member.name) > len(member.name) * 0.7:
        return True, "Nome suspeito (muitos números)"
    
    return False, None

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
    
    # VERIFICAÇÃO DE HIERARQUIA
    can_punish, target_role = can_moderate(ctx.author, usuario)
    if not can_punish:
        mod_role, mod_level = get_highest_staff_role(ctx.author)
        embed = discord.Embed(
            title="🛡️ Sem Permissão - Hierarquia",
            description=f"❌ **Você não pode advertir este usuário!**\n\n"
                       f"**Seu cargo:** {mod_role.mention if mod_role else 'Nenhum'}\n"
                       f"**Cargo do alvo:** {target_role.mention if target_role else 'Nenhum'}\n\n"
                       f"⚖️ **Regra:** Você só pode advertir membros com cargo **inferior** ao seu na hierarquia.\n\n"
                       f"**Hierarquia atual:**\n"
                       f"👑 [FND] Founder\n"
                       f"💎 [SDN] Sub Dono\n"
                       f"🔴 [ADM] Administrador\n"
                       f"🟠 [STF] Staff\n"
                       f"🟡 [MOD] Moderador\n"
                       f"🟢 [SBM] Sub Moderador\n"
                       f"⚪ Membro",
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
            name="📊 **RANK & XP**",
            value="`.help rank`\nSistema de níveis e ranking",
            inline=True
        )
        
        embed.add_field(
            name="📋 **INFORMAÇÕES**",
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
            name="💋 `.beijar @usuário`",
            value="**Beija** alguém com GIF animado\n*Romântico e fofo*",
            inline=True
        )
        
        embed.add_field(
            name="🤗 `.abracar @usuário`",
            value="**Abraça** alguém com GIF\n*Demonstre carinho*",
            inline=True
        )
        
        embed.add_field(
            name="😊 `.acariciar @usuário`",
            value="**Acaricia** alguém (head pat)\n*Relaxante e carinhoso*",
            inline=True
        )
        
        embed.add_field(
            name="👋 `.tapa @usuário`",
            value="**Dá um tapa** em alguém\n*Quando necessário*",
            inline=True
        )
        
        embed.add_field(
            name="💃 `.dancar [@usuário]`",
            value="**Dança** sozinho ou com alguém\n*Mostre seus passos!*",
            inline=True
        )
        
        embed.add_field(
            name="😭 `.chorar`",
            value="**Chora** dramaticamente\n*Às vezes necessário*",
            inline=True
        )
        
        embed.add_field(
            name="😌 `.cafune @usuário`",
            value="**Faz cafuné** em alguém\n*Relaxante*",
            inline=True
        )
        
        embed.add_field(
            name="💘 `.ship @user1 @user2`",
            value="**Shipa** duas pessoas\n*Veja a compatibilidade!*",
            inline=True
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
        
    elif categoria in ['rank', 'xp', 'nivel', 'nível', 'level']:
        embed = discord.Embed(
            title="📊 SISTEMA DE RANK & XP",
            description="**Sistema de níveis estilo Loritta!**\nGanhe XP conversando e suba de nível!\n\n**Como ganhar XP:**\n💬 Envie mensagens (+10-15 XP)\n⏱️ Cooldown: 60 segundos\n🚫 Spam não conta",
            color=0xff6600
        )
        
        embed.add_field(
            name="📊 `.rank [@usuário]`",
            value="**Ver rank** com card visual tipo Loritta\n*Mostra nível, XP, posição e progresso*\n**Exemplos:**\n• `.rank` - Seu rank\n• `.rank @user` - Rank de alguém",
            inline=False
        )
        
        embed.add_field(
            name="🏆 `.rankxp`",
            value="**Ver TOP 10** do servidor com imagem!\n*Ranking completo dos membros mais ativos*\n**Aliases:** `.leaderboard`, `.lb`, `.top`\n**Visual:** Card com barra de progresso",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ `.setxp @usuário <quantidade>`",
            value="**Definir XP** manualmente (Admin)\n*Modificar XP de qualquer usuário*\n**Exemplo:** `.setxp @user 1000`\n**Requer:** Permissão de Administrador",
            inline=False
        )
        
        embed.add_field(
            name="🎨 **DESIGN DO RANK CARD**",
            value="✅ Background laranja CAOS personalizado\n✅ Avatar circular do usuário\n✅ Barra de progresso animada\n✅ Nível e posição no ranking\n✅ Total de mensagens e XP",
            inline=False
        )
        
        embed.add_field(
            name="📈 **FÓRMULA DE XP**",
            value="**XP por nível:** 100 × (nível^1.5)\n**Exemplo:** Nível 10 = 3.162 XP\n**Sistema:** Exponencial tipo Loritta",
            inline=False
        )
        
        embed.set_thumbnail(url="https://i.ibb.co/BVX3K2Y2/1.png")
        embed.set_footer(text="📊 Sistema de XP • Totalmente automático")
        
    else:
        embed = discord.Embed(
            title="❌ CATEGORIA NÃO ENCONTRADA",
            description="**Categoria inválida!** Use uma das opções abaixo:",
            color=0xff0000
        )
        
        embed.add_field(
            name="📋 **CATEGORIAS DISPONÍVEIS**",
            value="• `moderacao` - Comandos de moderação\n• `advertencias` - Sistema de advertências\n• `mute` - Comandos de silenciamento\n• `diversao` - Comandos de diversão\n• `conversa` - Comandos sociais\n• `utilidades` - Comandos utilitários\n• `rank` - Sistema de XP e ranking",
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

# Configurações de ticket COMPLETAS (salvas em arquivo JSON)
ticket_config = {}

# Rastrear cooldown de criação de painel (anti-spam)
ticket_panel_cooldowns = {}  # {user_id: timestamp}

def get_default_ticket_config(guild_id):
    """Retorna configuração padrão de tickets"""
    return {
        'enabled': False,
        'category_id': None,
        'staff_role_ids': [],
        'log_channel_id': None,
        
        # Personalização do Painel
        'panel_title': '🎫 SISTEMA DE TICKETS',
        'panel_description': 'Clique no botão abaixo para abrir um ticket e falar com a equipe!',
        'panel_color': '0x5865F2',
        'button_text': 'Abrir Ticket',
        
        # Categorias Ativas (8 categorias)
        'categories_enabled': {
            'geral': True,
            'compras': True,
            'suporte': True,
            'denuncia': True,
            'parceria': True,
            'financeiro': True,
            'moderacao': True,
            'bug': True
        },
        
        # Customização de Categorias
        'categories_custom': {
            'geral': {'emoji': '📁', 'name': 'Geral', 'description': 'Assuntos gerais'},
            'compras': {'emoji': '🛒', 'name': 'Compras', 'description': 'Dúvidas sobre compras'},
            'suporte': {'emoji': '🔧', 'name': 'Suporte Técnico', 'description': 'Problemas técnicos'},
            'denuncia': {'emoji': '🚨', 'name': 'Denúncia', 'description': 'Reportar usuário/conteúdo'},
            'parceria': {'emoji': '🤝', 'name': 'Parceria', 'description': 'Proposta de parceria'},
            'financeiro': {'emoji': '💰', 'name': 'Financeiro', 'description': 'Questões de pagamento'},
            'moderacao': {'emoji': '🛡️', 'name': 'Moderação', 'description': 'Questões de moderação'},
            'bug': {'emoji': '🐛', 'name': 'Bug', 'description': 'Reportar bugs'}
        },
        
        # Sistema de Prioridades
        'priority_enabled': True,
        'priority_colors': True,  # Cores do embed baseadas na prioridade
        'priority_custom': {
            'baixa': {'emoji': '🟢', 'name': 'Baixa', 'description': 'Não é urgente', 'color': '0x00ff00'},
            'media': {'emoji': '🟡', 'name': 'Média', 'description': 'Prioridade normal', 'color': '0xffff00'},
            'alta': {'emoji': '🟠', 'name': 'Alta', 'description': 'Precisa de atenção', 'color': '0xff8800'},
            'urgente': {'emoji': '🔴', 'name': 'Urgente', 'description': 'Muito urgente!', 'color': '0xff0000'}
        },
        
        # Mensagens Customizáveis
        'message_welcome': 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.',
        'message_embed_main': 'Nossa equipe responderá o mais breve possível!',
        'message_closing': '🔒 Fechando ticket em 3 segundos...',
        'modal_title': '📋 Informações do Ticket',
        
        # Campos do Modal
        'field_subject_enabled': True,
        'field_description_enabled': True,
        'field_language_enabled': True,
        'field_additional_enabled': True,
        
        # Limites de caracteres
        'field_subject_max': 100,
        'field_description_max': 1000,
        'field_additional_max': 500,
        
        # Configurações Avançadas
        'ticket_limit_per_user': 1,
        'ticket_cooldown_minutes': 0,
        'transcript_enabled': True,
        'statistics_enabled': True,
        'rating_enabled': False,
        'mention_staff_on_create': False,
        
        # Logs
        'log_enabled': True,
        'log_include_stats': True,
        'log_attach_transcript': True,
        'log_show_participants': True,
        'log_show_duration': True
    }

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

# COMANDO .ticket REMOVIDO - USE O DASHBOARD WEB
# Acesse: https://caosbot-discord.onrender.com/dashboard
# Vá em "Tickets" e configure tudo pela interface web!

# TODAS AS VIEWS ANTIGAS DE TICKETS FORAM REMOVIDAS
# O sistema agora usa APENAS o sistema V2 com TicketPanelView, TicketConfigView (V2), etc
# Essas classes estão definidas mais acima no código

# ========================================
# SISTEMA DE PREFIXOS AUTOMÁTICOS
# ========================================

# FUNÇÃO DESABILITADA - CAUSAVA DUPLICAÇÕES
class PlaceholderOldTicketConfigView_REMOVED(discord.ui.View):
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
    

    def update_dropdowns(self):
        """Recria os dropdowns com placeholders atualizados"""
        # Limpar items
        self.clear_items()
        
        # Dropdown 1: Categoria (com placeholder atualizado)
        category_placeholder = f"{self.selected_category_emoji} {self.selected_category}" if self.selected_category else "🗂️ Selecione a Categoria do Ticket"
        category_select = discord.ui.Select(
            placeholder=category_placeholder,
            custom_id="category_dropdown",
            options=[
                discord.SelectOption(label="Geral", description="Assuntos gerais", emoji="📁", value="geral"),
                discord.SelectOption(label="Compras", description="Dúvidas sobre compras", emoji="🛒", value="compras"),
                discord.SelectOption(label="Suporte Técnico", description="Problemas técnicos", emoji="🔧", value="suporte"),
                discord.SelectOption(label="Denúncia", description="Reportar usuário/conteúdo", emoji="🚨", value="denuncia"),
                discord.SelectOption(label="Parceria", description="Proposta de parceria", emoji="🤝", value="parceria"),
                discord.SelectOption(label="Financeiro", description="Questões de pagamento", emoji="💰", value="financeiro"),
                discord.SelectOption(label="Moderação", description="Questões de moderação", emoji="🛡️", value="moderacao"),
                discord.SelectOption(label="Bug", description="Reportar bugs", emoji="🐛", value="bug"),
            ],
            row=0
        )
        category_select.callback = self.category_callback
        self.add_item(category_select)
        
        # Dropdown 2: Prioridade (com placeholder atualizado)
        priority_placeholder = f"{self.selected_priority_emoji} {self.selected_priority}" if self.selected_priority else "⚡ Selecione a Prioridade"
        priority_select = discord.ui.Select(
            placeholder=priority_placeholder,
            custom_id="priority_dropdown",
            options=[
                discord.SelectOption(label="Baixa", description="Não é urgente", emoji="🟢", value="baixa"),
                discord.SelectOption(label="Média", description="Prioridade normal", emoji="🟡", value="media"),
                discord.SelectOption(label="Alta", description="Precisa de atenção", emoji="🟠", value="alta"),
                discord.SelectOption(label="Urgente", description="Muito urgente!", emoji="🔴", value="urgente"),
            ],
            row=1
        )
        priority_select.callback = self.priority_callback
        self.add_item(priority_select)
        
        # Botão Continuar (habilitado se ambos selecionados)
        self.continue_button = discord.ui.Button(
            label="Continuar",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id="continue_button",
            row=2,
            disabled=not (self.selected_category and self.selected_priority)
        )
        self.continue_button.callback = self.continue_callback
        self.add_item(self.continue_button)

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

def run_discord_bot():
    """Executa o bot Discord em thread separada"""
    import time
    time.sleep(5)  # Aguarda Flask iniciar primeiro
    try:
        print('🚀 Iniciando bot Discord...')
        bot.run(TOKEN)
    except Exception as e:
        print(f'❌ Erro no bot Discord: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print('=' * 60)
    print('INICIANDO CAOS BOT - WEB SERVICE')
    print('=' * 60)
    
    # Verificar token principal
    if not TOKEN:
        print('ERRO: DISCORD_TOKEN nao encontrado!')
        exit(1)
    
    import os
    port = int(os.getenv("PORT", 10000))
    
    print(f'Porta: {port}')
    print(f'REDIRECT_URI: {DISCORD_REDIRECT_URI}')
    
    # Iniciar bot Discord em thread separada DEPOIS do Flask
    print('Iniciando bot Discord em background...')
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()
    
    # Flask como PROCESSO PRINCIPAL (BLOCKING - CRITICO!)
    print('Iniciando Flask como processo principal...')
    print('Flask vai rodar em modo blocking (correto para Web Service)')
    
    try:
        # MODO PRODUCTION - SEM DEBUG
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True  # Permite multiplas conexoes
        )
    except Exception as e:
        print(f'ERRO CRITICO NO FLASK: {e}')
        import traceback
        traceback.print_exc()
        exit(1)

# Sistema anti-hibernação já definido no início do arquivo

