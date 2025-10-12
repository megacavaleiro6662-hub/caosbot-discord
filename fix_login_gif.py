#!/usr/bin/env python3
# Script para corrigir GIF do login - tela toda, sem animações, só brilho laranja

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover estilo antigo do animated-bg e animações
old_gif_styles = """        /* GIF animado de fundo */
        .animated-bg {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 500px;
            height: 500px;
            opacity: 0.15;
            filter: hue-rotate(20deg) brightness(1.5) saturate(2);
            animation: pulse 3s ease-in-out infinite, rotate 20s linear infinite;
            z-index: 0;
            pointer-events: none;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                transform: translate(-50%, -50%) scale(1);
                filter: hue-rotate(20deg) brightness(1.5) saturate(2) drop-shadow(0 0 30px rgba(255, 100, 0, 0.8));
            }}
            50% {{
                transform: translate(-50%, -50%) scale(1.1);
                filter: hue-rotate(20deg) brightness(1.8) saturate(2.5) drop-shadow(0 0 50px rgba(255, 150, 0, 1));
            }}
        }}
        
        @keyframes rotate {{
            from {{ transform: translate(-50%, -50%) rotate(0deg); }}
            to {{ transform: translate(-50%, -50%) rotate(360deg); }}
        }}
        
        .login-container {{
            position: relative;
            z-index: 10;
        }}"""

new_gif_styles = """        /* GIF de fundo tela toda */
        .animated-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            opacity: 0.25;
            filter: hue-rotate(20deg) brightness(1.6) saturate(2.5) drop-shadow(0 0 40px rgba(255, 120, 0, 0.9));
            z-index: 0;
            pointer-events: none;
        }}
        
        .login-container {{
            position: relative;
            z-index: 10;
        }}"""

content = content.replace(old_gif_styles, new_gif_styles)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("GIF do login corrigido - tela toda sem animacoes!")
