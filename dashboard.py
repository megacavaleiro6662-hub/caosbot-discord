# ========================================
# DASHBOARD WEB COMPLETO - CAOS HUB
# ========================================
# Sistema moderno de gerenciamento via web
# - Dropdowns para canais/cargos (sem digitar IDs)
# - Sistema de toggle (ligar/desligar)
# - Integrado com painel de status do Discord
# - OAuth2 Discord para login

import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from functools import wraps
import discord
from discord.ext import commands
import asyncio
import threading

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET", "caos_hub_secret_key_2025")

# ========================================
# CONFIGURAÇÕES DO DISCORD OAUTH2
# ========================================

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "1417623469184516096")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "1yVL1ezvnlCabgljygymvzq6Hl7OfC6b")  # Pode sobrescrever com env
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")
BOT_TOKEN = os.getenv("DISCORD_TOKEN", "")  # Token do bot para API

DISCORD_API_URL = "https://discord.com/api/v10"
OAUTH2_URL = f"{DISCORD_API_URL}/oauth2/authorize"
TOKEN_URL = f"{DISCORD_API_URL}/oauth2/token"

# ID do servidor CAOS Hub (fixo)
GUILD_ID = "1365510151884378214"

# ========================================
# FUNÇÕES AUXILIARES - DISCORD API
# ========================================

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_info(access_token):
    """Busca informações do usuário"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{DISCORD_API_URL}/users/@me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_user_guilds(access_token):
    """Busca os servidores do usuário"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{DISCORD_API_URL}/users/@me/guilds", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_guild_channels():
    """Busca canais do servidor usando token do bot"""
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    response = requests.get(
        f"{DISCORD_API_URL}/guilds/{GUILD_ID}/channels",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return []

def get_guild_roles():
    """Busca cargos do servidor usando token do bot"""
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    response = requests.get(
        f"{DISCORD_API_URL}/guilds/{GUILD_ID}/roles",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return []

def get_guild_info():
    """Busca informações do servidor"""
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    response = requests.get(
        f"{DISCORD_API_URL}/guilds/{GUILD_ID}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return None

def is_admin(access_token):
    """Verifica se o usuário tem permissão de administrador no servidor"""
    user_guilds = get_user_guilds(access_token)
    
    for guild in user_guilds:
        if str(guild['id']) == GUILD_ID:
            # Verificar se tem permissão de administrador (bit 0x8)
            permissions = int(guild.get('permissions', 0))
            return bool(permissions & 0x8)
    
    return False

# ========================================
# GERENCIAMENTO DE CONFIGURAÇÕES
# ========================================

def load_ticket_config():
    """Carrega configuração de tickets"""
    try:
        with open('ticket_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(GUILD_ID, {
                'enabled': False,
                'category_id': None,
                'staff_role_ids': [],
                'welcome_message': 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.'
            })
    except:
        return {
            'enabled': False,
            'category_id': None,
            'staff_role_ids': [],
            'welcome_message': 'Olá! Obrigado por abrir um ticket. Nossa equipe responderá em breve.'
        }

def save_ticket_config(config):
    """Salva configuração de tickets"""
    try:
        with open('ticket_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    
    data[GUILD_ID] = config
    
    with open('ticket_config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_welcome_config():
    """Carrega configuração de boas-vindas"""
    try:
        with open('welcome_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'welcome_enabled': True,
            'goodbye_enabled': True,
            'autorole_enabled': True,
            'tickets_enabled': True,
            'status_message_id': None
        }

def save_welcome_config(config):
    """Salva configuração de boas-vindas"""
    with open('welcome_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# ========================================
# ROTAS - AUTENTICAÇÃO
# ========================================

@app.route('/')
def index():
    """Página inicial"""
    logged_in = 'user' in session
    user = session.get('user')
    guild_info = get_guild_info() if logged_in else None
    return render_template('index.html', logged_in=logged_in, user=user, guild=guild_info)

@app.route('/login')
def login():
    """Redireciona para o OAuth2 do Discord"""
    oauth_url = f"{OAUTH2_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds%20guilds.members.read"
    return redirect(oauth_url)

@app.route('/callback')
def callback():
    """Callback do OAuth2"""
    code = request.args.get('code')
    
    if not code:
        flash('❌ Erro: Código não fornecido', 'error')
        return redirect(url_for('index'))
    
    # Trocar código por token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if response.status_code != 200:
        flash(f'❌ Erro ao obter token: {response.text}', 'error')
        return redirect(url_for('index'))
    
    token_data = response.json()
    access_token = token_data['access_token']
    
    # Buscar informações do usuário
    user_data = get_user_info(access_token)
    
    if not user_data:
        flash('❌ Erro ao buscar informações do usuário', 'error')
        return redirect(url_for('index'))
    
    # Verificar se é administrador
    if not is_admin(access_token):
        flash('❌ Você precisa ser ADMINISTRADOR do servidor para acessar o dashboard!', 'error')
        return redirect(url_for('index'))
    
    # Salvar na sessão
    session['user'] = user_data
    session['access_token'] = access_token
    
    flash(f'✅ Bem-vindo, {user_data["username"]}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('👋 Você saiu do dashboard!', 'info')
    return redirect(url_for('index'))

# ========================================
# ROTAS - DASHBOARD
# ========================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    guild_info = get_guild_info()
    welcome_config = load_welcome_config()
    ticket_config = load_ticket_config()
    
    # Buscar info dos canais/cargos configurados
    channels = get_guild_channels()
    roles = get_guild_roles()
    
    # IDs configurados
    WELCOME_CHANNEL_ID = 1365848708532535369
    GOODBYE_CHANNEL_ID = 1365848742355275886
    AUTOROLE_ID = 1365630916927553586
    
    # Encontrar nomes
    welcome_channel = next((c for c in channels if c['id'] == str(WELCOME_CHANNEL_ID)), None)
    goodbye_channel = next((c for c in channels if c['id'] == str(GOODBYE_CHANNEL_ID)), None)
    autorole = next((r for r in roles if r['id'] == str(AUTOROLE_ID)), None)
    
    ticket_category = None
    if ticket_config.get('category_id'):
        ticket_category = next((c for c in channels if c['id'] == str(ticket_config['category_id'])), None)
    
    ticket_staff_roles = []
    if ticket_config.get('staff_role_ids'):
        ticket_staff_roles = [r for r in roles if r['id'] in [str(rid) for rid in ticket_config['staff_role_ids']]]
    
    return render_template('dashboard.html',
                         user=session['user'],
                         guild=guild_info,
                         welcome_config=welcome_config,
                         ticket_config=ticket_config,
                         welcome_channel=welcome_channel,
                         goodbye_channel=goodbye_channel,
                         autorole=autorole,
                         ticket_category=ticket_category,
                         ticket_staff_roles=ticket_staff_roles)

@app.route('/dashboard/tickets')
@login_required
def tickets_page():
    """Página de configuração de tickets"""
    channels = get_guild_channels()
    roles = get_guild_roles()
    ticket_config = load_ticket_config()
    
    # Filtrar apenas categorias
    categories = [ch for ch in channels if ch['type'] == 4]
    
    # Filtrar apenas cargos que não são @everyone e bots
    staff_roles = [r for r in roles if r['name'] != '@everyone' and not r.get('managed', False)]
    
    # Ordenar
    categories.sort(key=lambda x: x.get('position', 0))
    staff_roles.sort(key=lambda x: x.get('position', 0), reverse=True)
    
    return render_template('tickets.html',
                         user=session['user'],
                         categories=categories,
                         staff_roles=staff_roles,
                         ticket_config=ticket_config)

@app.route('/api/tickets/save', methods=['POST'])
@login_required
def save_tickets():
    """Salva configuração de tickets"""
    data = request.get_json()
    
    # Validar dados
    if not data:
        return jsonify({'success': False, 'message': '❌ Dados inválidos'}), 400
    
    # Carregar config atual
    ticket_config = load_ticket_config()
    welcome_config = load_welcome_config()
    
    # Atualizar configurações
    if 'enabled' in data:
        ticket_config['enabled'] = data['enabled']
        welcome_config['tickets_enabled'] = data['enabled']
    
    if 'category_id' in data:
        ticket_config['category_id'] = int(data['category_id']) if data['category_id'] else None
    
    if 'staff_role_ids' in data:
        ticket_config['staff_role_ids'] = [int(rid) for rid in data['staff_role_ids'] if rid]
    
    if 'welcome_message' in data:
        ticket_config['welcome_message'] = data['welcome_message']
    
    # Salvar
    save_ticket_config(ticket_config)
    save_welcome_config(welcome_config)
    
    return jsonify({'success': True, 'message': '✅ Configurações salvas com sucesso!'})

@app.route('/api/toggle/<system>', methods=['POST'])
@login_required
def toggle_system(system):
    """Liga/desliga sistemas (boas-vindas, saída, autorole, tickets)"""
    welcome_config = load_welcome_config()
    
    if system == 'welcome':
        welcome_config['welcome_enabled'] = not welcome_config['welcome_enabled']
        status = "✅ ATIVADO" if welcome_config['welcome_enabled'] else "❌ DESATIVADO"
        message = f'Sistema de boas-vindas: {status}'
    
    elif system == 'goodbye':
        welcome_config['goodbye_enabled'] = not welcome_config['goodbye_enabled']
        status = "✅ ATIVADO" if welcome_config['goodbye_enabled'] else "❌ DESATIVADO"
        message = f'Sistema de saída/ban: {status}'
    
    elif system == 'autorole':
        welcome_config['autorole_enabled'] = not welcome_config['autorole_enabled']
        status = "✅ ATIVADO" if welcome_config['autorole_enabled'] else "❌ DESATIVADO"
        message = f'Sistema de autorole: {status}'
    
    elif system == 'tickets':
        welcome_config['tickets_enabled'] = not welcome_config['tickets_enabled']
        status = "✅ ATIVADO" if welcome_config['tickets_enabled'] else "❌ DESATIVADO"
        message = f'Sistema de tickets: {status}'
        
        # Sincronizar com ticket_config
        ticket_config = load_ticket_config()
        ticket_config['enabled'] = welcome_config['tickets_enabled']
        save_ticket_config(ticket_config)
    
    else:
        return jsonify({'success': False, 'message': '❌ Sistema inválido'}), 400
    
    save_welcome_config(welcome_config)
    
    return jsonify({
        'success': True,
        'message': message,
        'enabled': welcome_config.get(f'{system}_enabled', False)
    })

# ========================================
# INICIAR SERVIDOR
# ========================================

if __name__ == '__main__':
    # Criar arquivos JSON se não existirem
    if not os.path.exists('ticket_config.json'):
        with open('ticket_config.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    if not os.path.exists('welcome_config.json'):
        with open('welcome_config.json', 'w', encoding='utf-8') as f:
            json.dump({
                'welcome_enabled': True,
                'goodbye_enabled': True,
                'autorole_enabled': True,
                'tickets_enabled': True,
                'status_message_id': None
            }, f)
    
    # Porta do ambiente (Render usa variável PORT)
    port = int(os.getenv('PORT', 5000))
    
    print('=' * 60)
    print('🚀 DASHBOARD CAOS HUB')
    print('=' * 60)
    print(f'🌐 Servidor iniciado na porta {port}')
    print(f'🔗 Acesse: http://localhost:{port}')
    print('📋 Faça login com sua conta do Discord!')
    print('=' * 60)
    
    app.run(debug=True, host='0.0.0.0', port=port)
