#!/usr/bin/env python3
# Script para adicionar comandos no help

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Texto antigo para substituir
old_text = '''        embed.add_field(
            name="🎯 **MAIS COMANDOS**",
            value="*Mais comandos de diversão em breve!*\\n*Sugestões são bem-vindas*",
            inline=False
        )'''

# Novo texto com todos os comandos
new_text = '''        embed.add_field(
            name="💋 `.beijar @usuário`",
            value="**Beija** alguém com GIF animado\\n*Romântico e fofo*",
            inline=True
        )
        
        embed.add_field(
            name="🤗 `.abracar @usuário`",
            value="**Abraça** alguém com GIF\\n*Demonstre carinho*",
            inline=True
        )
        
        embed.add_field(
            name="😊 `.acariciar @usuário`",
            value="**Acaricia** alguém (head pat)\\n*Relaxante e carinhoso*",
            inline=True
        )
        
        embed.add_field(
            name="👋 `.tapa @usuário`",
            value="**Dá um tapa** em alguém\\n*Quando necessário*",
            inline=True
        )
        
        embed.add_field(
            name="💃 `.dancar [@usuário]`",
            value="**Dança** sozinho ou com alguém\\n*Mostre seus passos!*",
            inline=True
        )
        
        embed.add_field(
            name="😭 `.chorar`",
            value="**Chora** dramaticamente\\n*Às vezes necessário*",
            inline=True
        )
        
        embed.add_field(
            name="😌 `.cafune @usuário`",
            value="**Faz cafuné** em alguém\\n*Relaxante*",
            inline=True
        )
        
        embed.add_field(
            name="💘 `.ship @user1 @user2`",
            value="**Shipa** duas pessoas\\n*Veja a compatibilidade!*",
            inline=True
        )'''

# Substituir
content = content.replace(old_text, new_text)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comandos adicionados no .help com sucesso!")
