"""
🎯 BANCO DE DADOS XP - SISTEMA TIPO LORITTA
SQLite/PostgreSQL com IDs corretos dos 8 níveis
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, BigInteger, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

Base = declarative_base()

# ==================== MODELOS ====================

class XPConfig(Base):
    """Configuração por servidor"""
    __tablename__ = 'xp_config'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    
    # Ativação
    is_enabled = Column(Boolean, default=False)
    
    # XP por mensagem
    min_xp = Column(Integer, default=5)
    max_xp = Column(Integer, default=15)
    cooldown = Column(Integer, default=30)
    
    # Anúncios (checkboxes - TODAS DESATIVADAS por padrão)
    announce_disabled = Column(Boolean, default=True)
    announce_current = Column(Boolean, default=False)
    announce_dm = Column(Boolean, default=False)
    announce_custom = Column(Boolean, default=False)
    announce_channel_id = Column(BigInteger, nullable=True)
    
    # Mensagem personalizada
    message_template = Column(Text, default='Parabéns {user_mention}! Você passou para o nível **{level}** ({level_name})! 🎉')
    message_type = Column(String(20), default='text')  # text, embed
    
    # Recompensas
    reward_mode = Column(String(20), default='replace')  # stack ou replace


class XPUser(Base):
    """Usuários com XP"""
    __tablename__ = 'xp_users'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_message_time = Column(DateTime, default=datetime.utcnow)


class XPLevel(Base):
    """Níveis e cargos"""
    __tablename__ = 'xp_levels'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    level = Column(Integer, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    required_xp = Column(Integer, nullable=False)


class XPMultiplier(Base):
    """Multiplicadores de XP por cargo"""
    __tablename__ = 'xp_multipliers'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    multiplier = Column(Float, default=1.0)


class XPBlockedRole(Base):
    """Cargos bloqueados"""
    __tablename__ = 'xp_blocked_roles'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)


class XPBlockedChannel(Base):
    """Canais bloqueados"""
    __tablename__ = 'xp_blocked_channels'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)


# ==================== DATABASE CLASS ====================

class XPDatabase:
    
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        if not database_url:
            database_url = 'sqlite:///xp_system.db'
        
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        print(f'✅ Banco XP inicializado')
    
    def get_session(self):
        return self.SessionLocal()
    
    # CONFIG
    def get_config(self, guild_id):
        session = self.get_session()
        try:
            config = session.query(XPConfig).filter_by(guild_id=guild_id).first()
            if not config:
                config = XPConfig(guild_id=guild_id)
                session.add(config)
                session.commit()
            return config
        finally:
            session.close()
    
    def update_config(self, guild_id, **kwargs):
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
    
    # USERS
    def get_user_xp(self, guild_id, user_id):
        session = self.get_session()
        try:
            return session.query(XPUser).filter_by(guild_id=guild_id, user_id=user_id).first()
        finally:
            session.close()
    
    def add_xp(self, guild_id, user_id, xp_amount):
        session = self.get_session()
        try:
            user = session.query(XPUser).filter_by(guild_id=guild_id, user_id=user_id).first()
            if not user:
                user = XPUser(guild_id=guild_id, user_id=user_id)
                session.add(user)
            
            user.xp += xp_amount
            user.total_messages += 1
            user.last_message_time = datetime.utcnow()
            
            # Calcular nível
            levels = self.get_levels(guild_id)
            new_level = 0
            for level_data in sorted(levels, key=lambda x: x.required_xp, reverse=True):
                if user.xp >= level_data.required_xp:
                    new_level = level_data.level
                    break
            
            old_level = user.level
            user.level = new_level
            
            session.commit()
            return old_level, new_level, user.xp
        finally:
            session.close()
    
    def reset_guild_xp(self, guild_id):
        session = self.get_session()
        try:
            session.query(XPUser).filter_by(guild_id=guild_id).delete()
            session.commit()
        finally:
            session.close()
    
    def get_leaderboard(self, guild_id, limit=10):
        session = self.get_session()
        try:
            return session.query(XPUser).filter_by(guild_id=guild_id).order_by(XPUser.xp.desc()).limit(limit).all()
        finally:
            session.close()
    
    # LEVELS
    def get_levels(self, guild_id):
        session = self.get_session()
        try:
            return session.query(XPLevel).filter_by(guild_id=guild_id).order_by(XPLevel.level).all()
        finally:
            session.close()
    
    def create_level(self, guild_id, level, role_id, role_name, required_xp):
        session = self.get_session()
        try:
            level_obj = XPLevel(
                guild_id=guild_id,
                level=level,
                role_id=role_id,
                role_name=role_name,
                required_xp=required_xp
            )
            session.add(level_obj)
            session.commit()
        finally:
            session.close()
    
    def delete_level(self, level_id):
        session = self.get_session()
        try:
            session.query(XPLevel).filter_by(id=level_id).delete()
            session.commit()
        finally:
            session.close()
    
    # MULTIPLIERS
    def get_multipliers(self, guild_id):
        session = self.get_session()
        try:
            return session.query(XPMultiplier).filter_by(guild_id=guild_id).all()
        finally:
            session.close()
    
    def add_multiplier(self, guild_id, role_id, role_name, multiplier):
        session = self.get_session()
        try:
            mult = XPMultiplier(guild_id=guild_id, role_id=role_id, role_name=role_name, multiplier=multiplier)
            session.add(mult)
            session.commit()
        finally:
            session.close()
    
    def delete_multiplier(self, mult_id):
        session = self.get_session()
        try:
            session.query(XPMultiplier).filter_by(id=mult_id).delete()
            session.commit()
        finally:
            session.close()
    
    # BLOCKED
    def get_blocked_roles(self, guild_id):
        session = self.get_session()
        try:
            return [b.role_id for b in session.query(XPBlockedRole).filter_by(guild_id=guild_id).all()]
        finally:
            session.close()
    
    def add_blocked_role(self, guild_id, role_id):
        session = self.get_session()
        try:
            blocked = XPBlockedRole(guild_id=guild_id, role_id=role_id)
            session.add(blocked)
            session.commit()
        finally:
            session.close()
    
    def remove_blocked_role(self, guild_id, role_id):
        session = self.get_session()
        try:
            session.query(XPBlockedRole).filter_by(guild_id=guild_id, role_id=role_id).delete()
            session.commit()
        finally:
            session.close()
    
    def get_blocked_channels(self, guild_id):
        session = self.get_session()
        try:
            return [b.channel_id for b in session.query(XPBlockedChannel).filter_by(guild_id=guild_id).all()]
        finally:
            session.close()
    
    def add_blocked_channel(self, guild_id, channel_id):
        session = self.get_session()
        try:
            blocked = XPBlockedChannel(guild_id=guild_id, channel_id=channel_id)
            session.add(blocked)
            session.commit()
        finally:
            session.close()
    
    def remove_blocked_channel(self, guild_id, channel_id):
        session = self.get_session()
        try:
            session.query(XPBlockedChannel).filter_by(guild_id=guild_id, channel_id=channel_id).delete()
            session.commit()
        finally:
            session.close()


xp_db = XPDatabase()
print('✅ XP Database pronta!')
