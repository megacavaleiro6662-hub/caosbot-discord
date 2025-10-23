"""
🌐 DASHBOARD WEB DO SISTEMA DE XP
FastAPI + OAuth Discord + Templates Jinja2
"""

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import aiohttp
import os
from datetime import datetime, timedelta
import csv
import io

from xp_database import xp_db

# ==================== CONFIGURAÇÃO ====================

app = FastAPI(title="XP System Dashboard")

# Session middleware (para OAuth)
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'sua-chave-secreta-super-segura'))

# Templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    print("⚠️ Pasta static não encontrada, criando...")
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

# OAuth Discord
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI_XP', 'http://localhost:8000/callback')
DISCORD_API_BASE = 'https://discord.com/api/v10'

# ==================== FUNÇÕES AUXILIARES ====================

async def get_discord_user(access_token):
    """Pega informações do usuário no Discord"""
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {access_token}'}
        async with session.get(f'{DISCORD_API_BASE}/users/@me', headers=headers) as response:
            if response.status == 200:
                return await response.json()
    return None

async def get_user_guilds(access_token):
    """Pega servidores do usuário"""
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {access_token}'}
        async with session.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=headers) as response:
            if response.status == 200:
                return await response.json()
    return []

async def get_guild_info(guild_id, bot_token):
    """Pega informações do servidor usando bot token"""
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bot {bot_token}'}
        async with session.get(f'{DISCORD_API_BASE}/guilds/{guild_id}', headers=headers) as response:
            if response.status == 200:
                return await response.json()
    return None

def check_admin(guild, user_id):
    """Verifica se usuário é admin do servidor"""
    # Verifica permissões (0x8 = Administrator)
    permissions = int(guild.get('permissions', 0))
    return (permissions & 0x8) == 0x8 or guild.get('owner_id') == user_id

# ==================== DEPENDÊNCIAS ====================

async def require_login(request: Request):
    """Verifica se o usuário está logado"""
    if 'access_token' not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session

async def require_admin(request: Request, guild_id: str):
    """Verifica se o usuário é admin do servidor"""
    session = await require_login(request)
    
    guilds = await get_user_guilds(session['access_token'])
    guild = next((g for g in guilds if g['id'] == guild_id), None)
    
    if not guild or not check_admin(guild, session['user']['id']):
        raise HTTPException(status_code=403, detail="No permission")
    
    return session

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.get("/")
async def home(request: Request):
    """Página inicial"""
    if 'user' in request.session:
        # Já está logado, redirecionar para dashboard
        return RedirectResponse(url="/servers")
    
    # URL de login do Discord
    oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "oauth_url": oauth_url
    })

@app.get("/callback")
async def oauth_callback(request: Request, code: str = None):
    """Callback do OAuth Discord"""
    if not code:
        return RedirectResponse(url="/")
    
    # Trocar código por token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{DISCORD_API_BASE}/oauth2/token', data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                access_token = token_data['access_token']
                
                # Pegar dados do usuário
                user = await get_discord_user(access_token)
                
                if user:
                    # Salvar na sessão
                    request.session['access_token'] = access_token
                    request.session['user'] = user
                    
                    return RedirectResponse(url="/servers")
    
    return RedirectResponse(url="/?error=login_failed")

@app.get("/logout")
async def logout(request: Request):
    """Fazer logout"""
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/servers", response_class=HTMLResponse)
async def servers_page(request: Request, session: dict = Depends(require_login)):
    """Lista de servidores do usuário"""
    guilds = await get_user_guilds(session['access_token'])
    
    # Filtrar apenas servidores onde o usuário é admin
    admin_guilds = [g for g in guilds if check_admin(g, session['user']['id'])]
    
    return templates.TemplateResponse("servers.html", {
        "request": request,
        "user": session['user'],
        "guilds": admin_guilds
    })

# ==================== ROTAS DO DASHBOARD ====================

@app.get("/dashboard/{guild_id}", response_class=HTMLResponse)
async def dashboard(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Dashboard principal do servidor"""
    config = xp_db.get_config(int(guild_id))
    levels = xp_db.get_levels(int(guild_id))
    
    # Estatísticas
    leaderboard = xp_db.get_leaderboard(int(guild_id), limit=10)
    total_users = len(xp_db.get_leaderboard(int(guild_id), limit=999999))
    
    # Boost ativo?
    boost = xp_db.get_active_boost(int(guild_id))
    
    return templates.TemplateResponse("xp_dashboard_full.html", {
        "request": request,
        "guild_id": guild_id,
        "config": config,
        "levels": levels,
        "leaderboard": leaderboard,
        "total_users": total_users,
        "boost": boost,
        "user": session['user']
    })

# ==================== API REST - CONFIGURAÇÃO GERAL ====================

@app.post("/api/xp/{guild_id}/config/general")
async def update_general_config(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Atualiza configuração geral"""
    data = await request.json()
    
    xp_db.update_config(
        int(guild_id),
        is_enabled=data.get('is_enabled', True),
        cooldown=data.get('cooldown', 30),
        min_xp=data.get('min_xp', 5),
        max_xp=data.get('max_xp', 15),
        log_channel=data.get('log_channel')
    )
    
    return {"success": True, "message": "Configuração atualizada!"}

# ==================== API REST - NÍVEIS E CARGOS ====================

@app.get("/api/xp/{guild_id}/levels")
async def get_levels_api(guild_id: str, session: dict = Depends(require_admin)):
    """Retorna todos os níveis"""
    levels = xp_db.get_levels(int(guild_id))
    return {
        "levels": [
            {
                "id": level.id,
                "level": level.level,
                "role_id": level.role_id,
                "role_name": level.role_name,
                "required_xp": level.required_xp,
                "multiplier": level.multiplier
            }
            for level in levels
        ]
    }

@app.post("/api/xp/{guild_id}/levels")
async def create_level(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Cria um novo nível"""
    from xp_database import XPLevel
    data = await request.json()
    
    session_db = xp_db.get_session()
    try:
        new_level = XPLevel(
            guild_id=int(guild_id),
            level=data['level'],
            role_id=int(data['role_id']),
            role_name=data['role_name'],
            required_xp=data['required_xp'],
            multiplier=data.get('multiplier', 1.0)
        )
        session_db.add(new_level)
        session_db.commit()
        return {"success": True, "message": "Nível criado!"}
    finally:
        session_db.close()

@app.put("/api/xp/{guild_id}/levels/{level_id}")
async def update_level(request: Request, guild_id: str, level_id: int, session: dict = Depends(require_admin)):
    """Atualiza um nível"""
    from xp_database import XPLevel
    data = await request.json()
    
    session_db = xp_db.get_session()
    try:
        level = session_db.query(XPLevel).filter_by(id=level_id, guild_id=int(guild_id)).first()
        if level:
            level.role_name = data.get('role_name', level.role_name)
            level.required_xp = data.get('required_xp', level.required_xp)
            level.multiplier = data.get('multiplier', level.multiplier)
            session_db.commit()
            return {"success": True, "message": "Nível atualizado!"}
        return {"success": False, "message": "Nível não encontrado"}
    finally:
        session_db.close()

@app.delete("/api/xp/{guild_id}/levels/{level_id}")
async def delete_level(guild_id: str, level_id: int, session: dict = Depends(require_admin)):
    """Deleta um nível"""
    from xp_database import XPLevel
    
    session_db = xp_db.get_session()
    try:
        level = session_db.query(XPLevel).filter_by(id=level_id, guild_id=int(guild_id)).first()
        if level:
            session_db.delete(level)
            session_db.commit()
            return {"success": True, "message": "Nível deletado!"}
        return {"success": False, "message": "Nível não encontrado"}
    finally:
        session_db.close()

# ==================== API REST - RECOMPENSAS ====================

@app.post("/api/xp/{guild_id}/config/rewards")
async def update_rewards_config(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Atualiza configuração de recompensas"""
    data = await request.json()
    
    xp_db.update_config(
        int(guild_id),
        reward_mode=data.get('reward_mode', 'stack'),
        bonus_on_levelup=data.get('bonus_on_levelup', 0)
    )
    
    return {"success": True, "message": "Recompensas atualizadas!"}

# ==================== API REST - BLOQUEIOS ====================

@app.post("/api/xp/{guild_id}/config/blocks")
async def update_blocks_config(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Atualiza cargos e canais bloqueados"""
    data = await request.json()
    
    blocked_roles = ','.join(map(str, data.get('blocked_roles', [])))
    blocked_channels = ','.join(map(str, data.get('blocked_channels', [])))
    
    xp_db.update_config(
        int(guild_id),
        blocked_roles=blocked_roles,
        blocked_channels=blocked_channels
    )
    
    return {"success": True, "message": "Bloqueios atualizados!"}

# ==================== API REST - MENSAGENS ====================

@app.post("/api/xp/{guild_id}/config/messages")
async def update_messages_config(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Atualiza configuração de mensagens"""
    data = await request.json()
    
    xp_db.update_config(
        int(guild_id),
        announce_mode=data.get('announce_mode', 'none'),
        announce_channel=data.get('announce_channel'),
        announce_type=data.get('announce_type', 'text'),
        message_template=data.get('message_template', '🎉 {user_mention} subiu para o nível **{level}**!')
    )
    
    return {"success": True, "message": "Mensagens atualizadas!"}

# ==================== API REST - RANK CARD ====================

@app.post("/api/xp/{guild_id}/config/rankcard")
async def update_rankcard_config(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Atualiza configuração da rank card"""
    data = await request.json()
    
    xp_db.update_config(
        int(guild_id),
        image_bg_color=data.get('image_bg_color', '#1a1a2e'),
        image_bg_url=data.get('image_bg_url'),
        image_bar_color=data.get('image_bar_color', '#0066ff'),
        image_text_color=data.get('image_text_color', '#ffffff')
    )
    
    return {"success": True, "message": "Rank card atualizada!"}

# ==================== API REST - BOOSTS ====================

@app.post("/api/xp/{guild_id}/boost")
async def create_boost(request: Request, guild_id: str, session: dict = Depends(require_admin)):
    """Cria um boost temporário"""
    data = await request.json()
    
    boost = xp_db.create_boost(
        int(guild_id),
        data.get('multiplier', 2.0),
        data.get('duration', 60)
    )
    
    return {
        "success": True,
        "message": "Boost ativado!",
        "boost": {
            "multiplier": boost.multiplier,
            "expires_at": boost.expires_at.isoformat()
        }
    }

# ==================== API REST - RESET ====================

@app.post("/api/xp/{guild_id}/reset")
async def reset_guild_xp(guild_id: str, session: dict = Depends(require_admin)):
    """Reseta XP de todo o servidor"""
    xp_db.reset_guild_xp(int(guild_id))
    return {"success": True, "message": "XP de todos os usuários foi resetado!"}

# ==================== API REST - ESTATÍSTICAS ====================

@app.get("/api/xp/{guild_id}/stats")
async def get_stats(guild_id: str, session: dict = Depends(require_admin)):
    """Retorna estatísticas do servidor"""
    from xp_database import XPUser, XPLog
    
    session_db = xp_db.get_session()
    try:
        users = session_db.query(XPUser).filter_by(guild_id=int(guild_id)).all()
        
        total_xp = sum(user.xp for user in users)
        total_messages = sum(user.total_messages for user in users)
        avg_xp = total_xp / len(users) if users else 0
        
        # Logs recentes
        logs = session_db.query(XPLog).filter_by(guild_id=int(guild_id)).order_by(XPLog.timestamp.desc()).limit(50).all()
        
        return {
            "total_users": len(users),
            "total_xp": total_xp,
            "total_messages": total_messages,
            "avg_xp": round(avg_xp, 2),
            "recent_logs": [
                {
                    "user_id": log.user_id,
                    "xp_gained": log.xp_gained,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ]
        }
    finally:
        session_db.close()

# ==================== EXPORTAÇÃO CSV ====================

@app.get("/api/xp/{guild_id}/export/csv")
async def export_csv(guild_id: str, session: dict = Depends(require_admin)):
    """Exporta ranking em CSV"""
    leaderboard = xp_db.get_leaderboard(int(guild_id), limit=999999)
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Posição', 'User ID', 'XP', 'Level', 'Total de Mensagens'])
    
    # Dados
    for idx, user in enumerate(leaderboard, start=1):
        writer.writerow([idx, user.user_id, user.xp, user.level, user.total_messages])
    
    # Retornar arquivo
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename=ranking_{guild_id}.csv'}
    )

# ==================== LEADERBOARD PÚBLICO ====================

@app.get("/leaderboard/{guild_id}", response_class=HTMLResponse)
async def public_leaderboard(request: Request, guild_id: str):
    """Página pública de leaderboard"""
    config = xp_db.get_config(int(guild_id))
    
    if not config.is_enabled:
        raise HTTPException(status_code=404, detail="XP system disabled")
    
    leaderboard = xp_db.get_leaderboard(int(guild_id), limit=100)
    levels = xp_db.get_levels(int(guild_id))
    
    return templates.TemplateResponse("leaderboard_public.html", {
        "request": request,
        "guild_id": guild_id,
        "leaderboard": leaderboard,
        "levels": levels
    })

# ==================== INICIALIZAÇÃO ====================

if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Iniciando Dashboard XP na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
