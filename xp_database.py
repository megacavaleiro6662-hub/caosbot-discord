"""
🗃️ BANCO DE DADOS DO SISTEMA DE XP
SQLAlchemy models para sistema de níveis e XP
"""

from sqlalchemy import create_engine, Column, BigInteger, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# ==================== TABELAS ====================

class XPUser(Base):
    """Tabela de XP dos usuários"""
    __tablename__ = 'xp_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    last_message_time = Column(DateTime, default=None)
    total_messages = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<XPUser guild={self.guild_id} user={self.user_id} xp={self.xp} level={self.level}>"


class XPConfig(Base):
    """Configurações gerais do sistema de XP por servidor"""
    __tablename__ = 'xp_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    # Sistema geral
    is_enabled = Column(Boolean, default=True)
    cooldown = Column(Integer, default=30)  # segundos
    min_xp = Column(Integer, default=5)
    max_xp = Column(Integer, default=15)
    
    # Recompensas
    reward_mode = Column(String(20), default='stack')  # 'stack' ou 'replace'
    bonus_on_levelup = Column(Integer, default=0)
    
    # Anúncios
    announce_mode = Column(String(20), default='none')  # 'none', 'current', 'dm', 'custom'
    announce_channel = Column(BigInteger, default=None)
    announce_type = Column(String(20), default='text')  # 'text', 'embed', 'image'
    message_template = Column(Text, default='🎉 {user_mention} subiu para o nível **{level}** ({level_name})! 🎊')
    
    # Bloqueios
    blocked_roles = Column(Text, default='')  # IDs separados por vírgula
    blocked_channels = Column(Text, default='')  # IDs separados por vírgula
    
    # Imagem
    image_bg_color = Column(String(7), default='#1a1a2e')
    image_bar_color = Column(String(7), default='#0066ff')
    image_text_color = Column(String(7), default='#ffffff')
    image_bg_url = Column(Text, default=None)
    
    # Log
    log_channel = Column(BigInteger, default=None)
    
    def __repr__(self):
        return f"<XPConfig guild={self.guild_id} enabled={self.is_enabled}>"


class XPLevel(Base):
    """Níveis e cargos de recompensa"""
    __tablename__ = 'xp_levels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    level = Column(Integer, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    required_xp = Column(Integer, nullable=False)
    multiplier = Column(Float, default=1.0)  # Multiplicador de XP para quem tem esse cargo
    
    def __repr__(self):
        return f"<XPLevel guild={self.guild_id} level={self.level} role={self.role_name}>"


class XPBoost(Base):
    """Boosts temporários de XP"""
    __tablename__ = 'xp_boosts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    multiplier = Column(Float, default=2.0)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<XPBoost guild={self.guild_id} multiplier={self.multiplier}x>"


class XPLog(Base):
    """Logs de ganho de XP"""
    __tablename__ = 'xp_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    xp_gained = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_id = Column(BigInteger, default=None)
    
    def __repr__(self):
        return f"<XPLog guild={self.guild_id} user={self.user_id} xp={self.xp_gained}>"


# ==================== DATABASE MANAGER ====================

class XPDatabase:
    """Gerenciador do banco de dados"""
    
    def __init__(self, database_url='sqlite:///xp_system.db'):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Retorna uma nova sessão"""
        return self.Session()
    
    # ==================== XP USERS ====================
    
    def get_user_xp(self, guild_id, user_id):
        """Pega XP do usuário"""
        session = self.get_session()
        try:
            user = session.query(XPUser).filter_by(
                guild_id=guild_id, user_id=user_id
            ).first()
            return user
        finally:
            session.close()
    
    def create_user_xp(self, guild_id, user_id):
        """Cria novo registro de XP"""
        session = self.get_session()
        try:
            user = XPUser(guild_id=guild_id, user_id=user_id, xp=0, level=1)
            session.add(user)
            session.commit()
            return user
        finally:
            session.close()
    
    def update_user_xp(self, guild_id, user_id, xp, level):
        """Atualiza XP do usuário"""
        session = self.get_session()
        try:
            user = session.query(XPUser).filter_by(
                guild_id=guild_id, user_id=user_id
            ).first()
            if user:
                user.xp = xp
                user.level = level
                user.last_message_time = datetime.utcnow()
                user.total_messages += 1
                session.commit()
        finally:
            session.close()
    
    def get_leaderboard(self, guild_id, limit=10):
        """Pega top usuários do servidor"""
        session = self.get_session()
        try:
            users = session.query(XPUser).filter_by(
                guild_id=guild_id
            ).order_by(XPUser.xp.desc()).limit(limit).all()
            return users
        finally:
            session.close()
    
    def reset_user_xp(self, guild_id, user_id):
        """Reseta XP de um usuário"""
        session = self.get_session()
        try:
            user = session.query(XPUser).filter_by(
                guild_id=guild_id, user_id=user_id
            ).first()
            if user:
                user.xp = 0
                user.level = 1
                session.commit()
        finally:
            session.close()
    
    def reset_guild_xp(self, guild_id):
        """Reseta XP de TODO o servidor"""
        session = self.get_session()
        try:
            session.query(XPUser).filter_by(guild_id=guild_id).delete()
            session.commit()
        finally:
            session.close()
    
    # ==================== XP CONFIG ====================
    
    def get_config(self, guild_id):
        """Pega configuração do servidor"""
        session = self.get_session()
        try:
            config = session.query(XPConfig).filter_by(guild_id=guild_id).first()
            if not config:
                # Criar config padrão
                config = XPConfig(guild_id=guild_id)
                session.add(config)
                session.commit()
            return config
        finally:
            session.close()
    
    def update_config(self, guild_id, **kwargs):
        """Atualiza configuração"""
        session = self.get_session()
        try:
            config = session.query(XPConfig).filter_by(guild_id=guild_id).first()
            if not config:
                config = XPConfig(guild_id=guild_id)
                session.add(config)
            
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            session.commit()
        finally:
            session.close()
    
    # ==================== XP LEVELS ====================
    
    def get_levels(self, guild_id):
        """Pega todos os níveis do servidor"""
        session = self.get_session()
        try:
            levels = session.query(XPLevel).filter_by(
                guild_id=guild_id
            ).order_by(XPLevel.level).all()
            return levels
        finally:
            session.close()
    
    def create_default_levels(self, guild_id):
        """Cria níveis padrão do prompt"""
        session = self.get_session()
        try:
            default_levels = [
                (1, 1365874242343800942, 'noob', 0, 1.0),
                (2, 1365874329010700359, 'bacon hair', 200, 1.0),
                (3, 1365874371280769084, 'pro', 500, 1.0),
                (4, 1365874770750738504, 'try harder', 1000, 2.0),
                (5, 1365875199265996921, 'épico', 2000, 1.5),
                (6, 1365874840405278730, 'místico', 4000, 1.5),
                (7, 1365874949562171402, 'lendário', 8000, 2.0),
                (8, 1365875021037441094, 'gilipado', 16000, 3.0),
            ]
            
            for level, role_id, role_name, required_xp, multiplier in default_levels:
                existing = session.query(XPLevel).filter_by(
                    guild_id=guild_id, level=level
                ).first()
                
                if not existing:
                    new_level = XPLevel(
                        guild_id=guild_id,
                        level=level,
                        role_id=role_id,
                        role_name=role_name,
                        required_xp=required_xp,
                        multiplier=multiplier
                    )
                    session.add(new_level)
            
            session.commit()
        finally:
            session.close()
    
    def get_level_by_xp(self, guild_id, xp):
        """Retorna o nível baseado no XP"""
        session = self.get_session()
        try:
            levels = session.query(XPLevel).filter_by(
                guild_id=guild_id
            ).filter(XPLevel.required_xp <= xp).order_by(XPLevel.required_xp.desc()).first()
            return levels
        finally:
            session.close()
    
    # ==================== XP BOOSTS ====================
    
    def get_active_boost(self, guild_id):
        """Pega boost ativo"""
        session = self.get_session()
        try:
            boost = session.query(XPBoost).filter_by(
                guild_id=guild_id
            ).filter(XPBoost.expires_at > datetime.utcnow()).first()
            return boost
        finally:
            session.close()
    
    def create_boost(self, guild_id, multiplier, duration_minutes):
        """Cria um boost temporário"""
        from datetime import timedelta
        session = self.get_session()
        try:
            expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            boost = XPBoost(
                guild_id=guild_id,
                multiplier=multiplier,
                expires_at=expires_at
            )
            session.add(boost)
            session.commit()
            return boost
        finally:
            session.close()


# ==================== INSTÂNCIA GLOBAL ====================

# Usar PostgreSQL no Render ou SQLite local
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///xp_system.db')

# Fix para Render (postgres:// → postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

xp_db = XPDatabase(DATABASE_URL)

print('✅ Banco de dados XP inicializado!')
