"""
💬 COMANDOS DO SISTEMA DE XP
.xp, .xprank, .xpreset, .xpboost, etc
"""

import discord
from discord.ext import commands
from xp_database import xp_db
from image_generator import generate_rank_card, generate_leaderboard_image
import asyncio

# ==================== COMANDOS ====================

class XPCommands(commands.Cog):
    """Cog com todos os comandos de XP"""
    
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
    
    @commands.command(name='xpreset')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def xpreset_command(self, ctx, member: discord.Member = None):
        """
        Reseta o XP de um usuário (apenas administradores)
        
        Uso: .xpreset @usuário
        """
        
        if not member:
            await ctx.send('❌ Você precisa mencionar um usuário! Exemplo: `.xpreset @User`')
            return
        
        # Confirmação
        embed = discord.Embed(
            title='⚠️ Confirmar Reset de XP',
            description=f'Tem certeza que deseja resetar o XP de {member.mention}?\n\nReaja com ✅ para confirmar ou ❌ para cancelar.',
            color=0xff9900
        )
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == msg.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == '✅':
                # Resetar XP
                xp_db.reset_user_xp(ctx.guild.id, member.id)
                
                embed = discord.Embed(
                    title='✅ XP Resetado',
                    description=f'O XP de {member.mention} foi resetado para 0!',
                    color=0x00ff00
                )
                await msg.edit(embed=embed)
                
                # Remover cargos de nível
                levels_config = xp_db.get_levels(ctx.guild.id)
                for level_data in levels_config:
                    role = ctx.guild.get_role(level_data.role_id)
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason='XP resetado')
                        except:
                            pass
            else:
                embed = discord.Embed(
                    title='❌ Cancelado',
                    description='Reset de XP cancelado.',
                    color=0xff0000
                )
                await msg.edit(embed=embed)
        
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title='⏱️ Timeout',
                description='Tempo esgotado. Operação cancelada.',
                color=0x888888
            )
            await msg.edit(embed=embed)
    
    @commands.command(name='xpresetall')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def xpresetall_command(self, ctx):
        """
        Reseta o XP de TODOS os usuários (apenas administradores)
        
        Uso: .xpresetall
        """
        
        # Confirmação DUPLA
        embed = discord.Embed(
            title='🚨 ATENÇÃO - RESET TOTAL',
            description='⚠️ **ESTA AÇÃO É IRREVERSÍVEL!**\n\nVocê está prestes a **DELETAR TODO O XP** de **TODOS OS USUÁRIOS** deste servidor!\n\nDigite `CONFIRMAR RESET` para continuar ou `cancelar` para abortar.',
            color=0xff0000
        )
        
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            if msg.content.upper() == 'CONFIRMAR RESET':
                # Reset total
                xp_db.reset_guild_xp(ctx.guild.id)
                
                embed = discord.Embed(
                    title='✅ XP Total Resetado',
                    description='Todo o XP do servidor foi resetado!',
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
                
                print(f'⚠️ XP TOTAL RESETADO no servidor {ctx.guild.name} por {ctx.author}')
            
            else:
                await ctx.send('❌ Operação cancelada.')
        
        except asyncio.TimeoutError:
            await ctx.send('⏱️ Timeout. Operação cancelada.')
    
    @commands.command(name='xpboost')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def xpboost_command(self, ctx, multiplier: float = 2.0, duration: int = 60):
        """
        Ativa um boost temporário de XP (apenas administradores)
        
        Uso: .xpboost [multiplicador] [duração em minutos]
        Exemplo: .xpboost 2.0 120  (2x XP por 2 horas)
        """
        
        # Validar valores
        multiplier = max(1.0, min(multiplier, 10.0))
        duration = max(1, min(duration, 10080))  # Máx 1 semana
        
        # Criar boost
        boost = xp_db.create_boost(ctx.guild.id, multiplier, duration)
        
        embed = discord.Embed(
            title='🚀 Boost de XP Ativado!',
            description=f'**Multiplicador:** {multiplier}x\n**Duração:** {duration} minutos\n**Expira:** <t:{int(boost.expires_at.timestamp())}:R>',
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
        
        # Anunciar no servidor (se tiver canal configurado)
        config = xp_db.get_config(ctx.guild.id)
        if config.log_channel:
            log_channel = ctx.guild.get_channel(config.log_channel)
            if log_channel:
                try:
                    await log_channel.send(f'🎉 **BOOST DE XP ATIVADO!** Ganhe {multiplier}x mais XP pelos próximos {duration} minutos!')
                except:
                    pass
    
    @commands.command(name='xpconfig')
    @commands.guild_only()
    async def xpconfig_command(self, ctx):
        """
        Mostra a configuração atual do sistema de XP (apenas leitura)
        
        Uso: .xpconfig
        """
        
        config = xp_db.get_config(ctx.guild.id)
        
        embed = discord.Embed(
            title=f'⚙️ Configuração de XP - {ctx.guild.name}',
            color=0x0066ff
        )
        
        # Status
        status = '✅ Ativado' if config.is_enabled else '❌ Desativado'
        embed.add_field(name='Status', value=status, inline=True)
        
        # XP por mensagem
        embed.add_field(name='XP por Mensagem', value=f'{config.min_xp}–{config.max_xp}', inline=True)
        
        # Cooldown
        embed.add_field(name='Cooldown', value=f'{config.cooldown}s', inline=True)
        
        # Modo de recompensa
        mode_text = '📚 Empilhar cargos' if config.reward_mode == 'stack' else '🔄 Substituir cargo'
        embed.add_field(name='Modo de Recompensa', value=mode_text, inline=True)
        
        # Anúncio
        announce_modes = {
            'none': '🚫 Nenhum',
            'current': '💬 Canal atual',
            'dm': '📧 Mensagem direta',
            'custom': '📍 Canal personalizado'
        }
        embed.add_field(name='Anúncio de Level Up', value=announce_modes.get(config.announce_mode, 'none'), inline=True)
        
        # Boost ativo?
        boost = xp_db.get_active_boost(ctx.guild.id)
        if boost:
            embed.add_field(
                name='🚀 Boost Ativo',
                value=f'{boost.multiplier}x até <t:{int(boost.expires_at.timestamp())}:R>',
                inline=True
            )
        
        # Total de usuários com XP
        leaderboard = xp_db.get_leaderboard(ctx.guild.id, limit=999999)
        embed.add_field(name='👥 Usuários com XP', value=len(leaderboard), inline=True)
        
        embed.set_footer(text='Configure tudo no dashboard web!')
        
        await ctx.send(embed=embed)
    
    @commands.command(name='xpsetup')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def xpsetup_command(self, ctx):
        """
        Cria os níveis padrão e inicializa o sistema (apenas administradores)
        
        Uso: .xpsetup
        """
        
        # Criar níveis padrão
        xp_db.create_default_levels(ctx.guild.id)
        
        # Criar/atualizar config
        xp_db.update_config(ctx.guild.id, is_enabled=True)
        
        embed = discord.Embed(
            title='✅ Sistema de XP Configurado!',
            description='Os 8 níveis padrão foram criados:\n\n'
                        '**1.** noob (0 XP)\n'
                        '**2.** bacon hair (200 XP)\n'
                        '**3.** pro (500 XP)\n'
                        '**4.** try harder (1,000 XP) • 2x XP\n'
                        '**5.** épico (2,000 XP) • 1.5x XP\n'
                        '**6.** místico (4,000 XP) • 1.5x XP\n'
                        '**7.** lendário (8,000 XP) • 2x XP\n'
                        '**8.** gilipado (16,000 XP) • 3x XP\n\n'
                        '🌐 Acesse o **dashboard web** para personalizar tudo!',
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)


# ==================== SETUP ====================

async def setup(bot):
    """Adiciona os comandos ao bot"""
    await bot.add_cog(XPCommands(bot))


print('✅ Comandos de XP carregados!')
