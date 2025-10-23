"""
💎 COMANDOS DE XP (APENAS VISUALIZAÇÃO)
.xp, .xp @user, .xprank
"""

import discord
from discord.ext import commands
from xp_database import xp_db
from image_generator import generate_rank_card, generate_leaderboard_image

class XPCommands(commands.Cog):
    """Comandos de visualização de XP"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='xp', aliases=['rank', 'level'])
    @commands.guild_only()
    async def xp_command(self, ctx, member: discord.Member = None):
        """Ver rank card (imagem)"""
        
        if not member:
            member = ctx.author
        
        config = xp_db.get_config(ctx.guild.id)
        
        if not config.is_enabled:
            await ctx.send('❌ O sistema de XP está desativado.')
            return
        
        user_data = xp_db.get_user_xp(ctx.guild.id, member.id)
        
        if not user_data or user_data.xp == 0:
            await ctx.send(f'❌ {member.mention} ainda não tem XP registrado.')
            return
        
        # Gerar imagem
        async with ctx.typing():
            rank_card = await generate_rank_card(member, ctx.guild.id, config)
        
        if rank_card:
            await ctx.send(file=rank_card)
        else:
            await ctx.send('❌ Erro ao gerar rank card.')
    
    @commands.command(name='xprank', aliases=['leaderboard', 'top'])
    @commands.guild_only()
    async def xprank_command(self, ctx, limit: int = 10):
        """Ver top 10 (imagem)"""
        
        limit = max(1, min(limit, 25))
        
        config = xp_db.get_config(ctx.guild.id)
        
        if not config.is_enabled:
            await ctx.send('❌ O sistema de XP está desativado.')
            return
        
        top_users = xp_db.get_leaderboard(ctx.guild.id, limit=limit)
        
        if not top_users:
            await ctx.send('❌ Ainda não há usuários com XP.')
            return
        
        # Gerar imagem
        async with ctx.typing():
            leaderboard_image = await generate_leaderboard_image(
                self.bot, ctx.guild, top_users, config
            )
        
        if leaderboard_image:
            await ctx.send(file=leaderboard_image)
        else:
            await ctx.send('❌ Erro ao gerar leaderboard.')


async def setup(bot):
    """Adiciona os comandos"""
    await bot.add_cog(XPCommands(bot))


print('✅ Comandos XP carregados (apenas visualização)!')
