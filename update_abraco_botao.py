#!/usr/bin/env python3
# Script para atualizar GIFs de abraço e adicionar sistema de botões

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Atualizar GIFs de abraço
old_hug_gifs = """    'hug': [
        'https://media.tenor.com/KZLA62pS29gAAAAM/hug-anime.gif',
        'https://media.tenor.com/tKj2V0C4o_AAAAAM/anime-hug.gif',
        'https://media.tenor.com/Kry0v9GAGzsAAAAM/hug-anime.gif',
        'https://media.tenor.com/MJjV9h94xkIAAAAM/anime-hug.gif',
        'https://media.tenor.com/J4mHTDPaGFQAAAAM/anime-hug.gif'
    ]"""

new_hug_gifs = """    'hug': [
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lrr9rHuoJOE0w/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/49mdjsMrH7oze/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QFPoctlgZ5s0E/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PHZ7v9tfQu0o0/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lrr9rHuoJOE0w/giphy.gif',
        'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2NocHBpNXA4enpkYWdpM21raGc3aTFoOTlwYW52aTE1bjVxbGNpNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3bqtLDeiDtwhq/giphy.gif'
    ]"""

content = content.replace(old_hug_gifs, new_hug_gifs)

# 2. Adicionar classes de View com botões (antes dos comandos)
view_classes = """
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

"""

# Encontrar onde inserir (antes do @bot.command(name='beijar'))
insert_position = content.find("@bot.command(name='beijar')")
if insert_position != -1:
    content = content[:insert_position] + view_classes + content[insert_position:]

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("GIFs de abraco atualizados e View de botoes adicionada!")
