"""
🎯 BANCO DE DADOS DO SISTEMA XP
SQLAlchemy com SQLite/PostgreSQL
IDs CORRETOS dos cargos do servidor
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, BigInteger, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

Base = declarative_base()

# ==================== MODELOS ====================

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


class XPConfig(Base):
    """Configuração por servidor"""
    __tablename__ = 'xp_config'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    
    # Geral
    is_enabled = Column(Boolean, default=True)
    cooldown = Column(Integer, default=30)  # segundos
    min_xp = Column(Integer, default=5)
    max_xp = Column(Integer, default=15)
    
    # Anúncios (checkboxes - podem ter múltiplos ativos)
    announce_current_channel = Column(Boolean, default=True)
    announce_dm = Column(Boolean, default=False)
    announce_custom_channel = Column(Boolean, default=False)
    announce_channel_id = Column(BigInteger, nullable=True)
    
    # Mensagem personalizada
    message_template = Column(Text, default='🎉 {user_mention} subiu para o nível **{level}** ({level_name})!')
    message_type = Column(String(20), default='text')  # text, embed, image
    
    # Recompensas
    reward_mode = Column(String(20), default='stack')  # stack ou replace
    
    # Rank card
    image_bg_color = Column(String(7), default='#1a1a2e')
    image_bg_url = Column(Text, nullable=True)
    image_bar_color = Column(String(7), default='#0066ff')
    image_text_color = Column(String(7), default='#ffffff')
    
    # Log
    log_channel_id = Column(BigInteger, nullable=True)


class XPLevel(Base):
    """Níveis e cargos"""
    __tablename__ = 'xp_levels'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    level = Column(Integer, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    required_xp = Column(Integer, nullable=False)
    xp_reward = Column(Integer, default=0)  # XP extra ao alcançar esse nível


class XPMultiplier(Base):
    """Multiplicadores de XP por cargo"""
    __tablename__ = 'xp_multipliers'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    multiplier = Column(Float, default=1.0)


class XPBlockedRole(Base):
    """Cargos bloqueados (não ganham XP)"""
    __tablename__ = 'xp_blocked_roles'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)


class XPBlockedChannel(Base):
    """Canais bloqueados (não ganham XP)"""
    __tablename__ = 'xp_blocked_channels'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)


class XPBoost(Base):
    """Boosts temporários de XP"""
    __tablename__ = 'xp_boosts'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    multiplier = Column(Float, nullable=False)
    expires_at = Column(DateTime, nullable=False)


# ==================== DATABASE CLASS ====================

class XPDatabase:
    """Gerenciador do banco de dados"""
    
    def __init__(self):
        # Usar PostgreSQL no Render, SQLite local
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        if not database_url:
            database_url = 'sqlite:///xp_system.db'
        
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        print(f'✅ Banco XP inicializado: {database_url}')
    
    def get_session(self):
        """Retorna uma sessão do banco"""
        return self.SessionLocal()
    
    # ==================== CONFIG ====================
    
    def get_config(self, guild_id):
        """Pega config do servidor"""
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
        """Atualiza config"""
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
    
    # ==================== USERS ====================
    
    def get_user_xp(self, guild_id, user_id):
        """Pega XP do usuário"""
        session = self.get_session()
        try:
            return session.query(XPUser).filter_by(guild_id=guild_id, user_id=user_id).first()
        finally:
            session.close()
    
    def add_xp(self, guild_id, user_id, xp_amount):
        """Adiciona XP e calcula nível"""
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
    
    def reset_user_xp(self, guild_id, user_id):
        """Reseta XP de um usuário"""
        session = self.get_session()
        try:
            user = session.query(XPUser).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.xp = 0
                user.level = 0
                session.commit()
        finally:
            session.close()
    
    def reset_guild_xp(self, guild_id):
        """Reseta XP de todos no servidor"""
        session = self.get_session()
        try:
            session.query(XPUser).filter_by(guild_id=guild_id).delete()
            session.commit()
        finally:
            session.close()
    
    def get_leaderboard(self, guild_id, limit=10):
        """Pega leaderboard"""
        session = self.get_session()
        try:
            return session.query(XPUser).filter_by(guild_id=guild_id).order_by(XPUser.xp.desc()).limit(limit).all()
        finally:
            session.close()
    
    # ==================== LEVELS ====================
    
    def get_levels(self, guild_id):
        """Pega todos os níveis"""
        session = self.get_session()
        try:
            return session.query(XPLevel).filter_by(guild_id=guild_id).order_by(XPLevel.level).all()
        finally:
            session.close()
    
    def create_default_levels(self, guild_id):
        """Cria os 8 níveis padrão com IDs CORRETOS"""
        session = self.get_session()
        try:
            # Deletar níveis existentes
            session.query(XPLevel).filter_by(guild_id=guild_id).delete()
            
            # IDs CORRETOS do prompt
            levels_data = [
                (1, 1365874242343800942, 'noob', 0, 0),
                (2, 1365874329010700359, 'bacon hair', 200, 50),
                (3, 1365874371280769084, 'pro', 500, 100),
                (4, 1365874770750738504, 'try harder', 1000, 200),
                (5, 1365875199265996921, 'épico', 2000, 300),
                (6, 1365874840405278730, 'místico', 4000, 500),
                (7, 1365874949562171402, 'lendário', 8000, 800),
                (8, 1365875021037441094, 'gilipado', 16000, 1000),
            ]
            
            for level, role_id, role_name, required_xp, xp_reward in levels_data:
                level_obj = XPLevel(
                    guild_id=guild_id,
                    level=level,
                    role_id=role_id,
                    role_name=role_name,
                    required_xp=required_xp,
                    xp_reward=xp_reward
                )
                session.add(level_obj)
            
            session.commit()
            print(f'✅ 8 níveis criados para guild {guild_id}')
        finally:
            session.close()
    
    # ==================== MULTIPLIERS ====================
    
    def get_multipliers(self, guild_id):
        """Pega multiplicadores"""
        session = self.get_session()
        try:
            return session.query(XPMultiplier).filter_by(guild_id=guild_id).all()
        finally:
            session.close()
    
    def add_multiplier(self, guild_id, role_id, role_name, multiplier):
        """Adiciona multiplicador"""
        session = self.get_session()
        try:
            mult = XPMultiplier(guild_id=guild_id, role_id=role_id, role_name=role_name, multiplier=multiplier)
            session.add(mult)
            session.commit()
        finally:
            session.close()
    
    def delete_multiplier(self, mult_id):
        """Deleta multiplicador"""
        session = self.get_session()
        try:
            session.query(XPMultiplier).filter_by(id=mult_id).delete()
            session.commit()
        finally:
            session.close()
    
    # ==================== BLOCKED ====================
    
    def get_blocked_roles(self, guild_id):
        """Pega cargos bloqueados"""
        session = self.get_session()
        try:
            return [b.role_id for b in session.query(XPBlockedRole).filter_by(guild_id=guild_id).all()]
        finally:
            session.close()
    
    def add_blocked_role(self, guild_id, role_id):
        """Bloqueia cargo"""
        session = self.get_session()
        try:
            blocked = XPBlockedRole(guild_id=guild_id, role_id=role_id)
            session.add(blocked)
            session.commit()
        finally:
            session.close()
    
    def remove_blocked_role(self, guild_id, role_id):
        """Desbloqueia cargo"""
        session = self.get_session()
        try:
            session.query(XPBlockedRole).filter_by(guild_id=guild_id, role_id=role_id).delete()
            session.commit()
        finally:
            session.close()
    
    def get_blocked_channels(self, guild_id):
        """Pega canais bloqueados"""
        session = self.get_session()
        try:
            return [b.channel_id for b in session.query(XPBlockedChannel).filter_by(guild_id=guild_id).all()]
        finally:
            session.close()
    
    def add_blocked_channel(self, guild_id, channel_id):
        """Bloqueia canal"""
        session = self.get_session()
        try:
            blocked = XPBlockedChannel(guild_id=guild_id, channel_id=channel_id)
            session.add(blocked)
            session.commit()
        finally:
            session.close()
    
    def remove_blocked_channel(self, guild_id, channel_id):
        """Desbloqueia canal"""
        session = self.get_session()
        try:
            session.query(XPBlockedChannel).filter_by(guild_id=guild_id, channel_id=channel_id).delete()
            session.commit()
        finally:
            session.close()
    
    # ==================== BOOSTS ====================
    
    def get_active_boost(self, guild_id):
        """Pega boost ativo"""
        session = self.get_session()
        try:
            boost = session.query(XPBoost).filter(
                XPBoost.guild_id == guild_id,
                XPBoost.expires_at > datetime.utcnow()
            ).first()
            return boost
        finally:
            session.close()
    
    def create_boost(self, guild_id, multiplier, duration_minutes):
        """Cria boost temporário"""
        session = self.get_session()
        try:
            # Remover boosts antigos
            session.query(XPBoost).filter_by(guild_id=guild_id).delete()
            
            expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            boost = XPBoost(guild_id=guild_id, multiplier=multiplier, expires_at=expires_at)
            session.add(boost)
            session.commit()
            return boost
        finally:
            session.close()


# ==================== INSTÂNCIA GLOBAL ====================

xp_db = XPDatabase()
print('✅ XP Database pronta!')
