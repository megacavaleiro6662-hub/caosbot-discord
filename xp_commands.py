"""
💬 COMANDOS DO SISTEMA DE XP
Apenas comandos de VISUALIZAÇÃO (sem configuração)
.xp, .xprank - Configure TUDO no dashboard web!
"""

import discord
from discord.ext import commands
from xp_database import xp_db
from image_generator import generate_rank_card, generate_leaderboard_image

# ==================== COMANDOS ====================

class XPCommands(commands.Cog):
    """Cog com comandos de visualização de XP (sem admin)"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='xp', aliases=['rank', 'level'])
    @commands.guild_only()
    async def xp_command(self, ctx, member: discord.Member = None):
        """
        Mostra o XP e nível do usuário em uma imagem
        
        Uso: .xp [@usuário]
        """
        
        # Se não especificar, mostra do próprio usuário
        if not member:
            member = ctx.author
        
        # Buscar configuração
        config = xp_db.get_config(ctx.guild.id)
        
        if not config.is_enabled:
            await ctx.send('❌ O sistema de XP está desativado neste servidor.')
            return
        
        # Verificar se o usuário tem XP
        user_data = xp_db.get_user_xp(ctx.guild.id, member.id)
        
        if not user_data or user_data.xp == 0:
            await ctx.send(f'❌ {member.mention} ainda não tem XP registrado.')
            return
        
        # Gerar rank card
        async with ctx.typing():
            rank_card = await generate_rank_card(member, ctx.guild.id, config)
        
        if rank_card:
            await ctx.send(file=rank_card)
        else:
            # Fallback para embed
            levels_config = xp_db.get_levels(ctx.guild.id)
            current_level_data = None
            
            for level_data in levels_config:
                if level_data.level == user_data.level:
                    current_level_data = level_data
                    break
            
            embed = discord.Embed(
                title=f'📊 XP de {member.name}',
                color=0x0066ff
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='⭐ Nível', value=user_data.level, inline=True)
            embed.add_field(name='💎 XP Total', value=f'{user_data.xp:,}', inline=True)
            
            if current_level_data:
                embed.add_field(name='🏷️ Cargo', value=current_level_data.role_name, inline=True)
            
            await ctx.send(embed=embed)
    
    @commands.command(name='xprank', aliases=['leaderboard', 'top'])
    @commands.guild_only()
    async def xprank_command(self, ctx, limit: int = 10):
        """
        Mostra o ranking de XP do servidor
        
        Uso: .xprank [quantidade]
        """
        
        # Limitar entre 1 e 25
        limit = max(1, min(limit, 25))
        
        # Buscar configuração
        config = xp_db.get_config(ctx.guild.id)
        
        if not config.is_enabled:
            await ctx.send('❌ O sistema de XP está desativado neste servidor.')
            return
        
        # Buscar top usuários
        top_users = xp_db.get_leaderboard(ctx.guild.id, limit=limit)
        
        if not top_users:
            await ctx.send('❌ Ainda não há usuários com XP registrado.')
            return
        
        # Gerar imagem do leaderboard
        async with ctx.typing():
            leaderboard_image = await generate_leaderboard_image(
                self.bot, ctx.guild, top_users, config
            )
        
        if leaderboard_image:
            await ctx.send(file=leaderboard_image)
        else:
            # Fallback para texto
            embed = discord.Embed(
                title=f'🏆 Top {limit} - {ctx.guild.name}',
                color=0x0066ff
            )
            
            description = ''
            for idx, user_data in enumerate(top_users, start=1):
                try:
                    member = ctx.guild.get_member(user_data.user_id)
                    if member:
                        description += f'**#{idx}** {member.mention} • Level {user_data.level} • {user_data.xp:,} XP\n'
                except:
                    continue
            
            embed.description = description
            await ctx.send(embed=embed)


# ==================== SETUP ====================

async def setup(bot):
    """Adiciona os comandos ao bot"""
    await bot.add_cog(XPCommands(bot))


print('✅ Comandos de XP carregados (apenas visualização)!')
