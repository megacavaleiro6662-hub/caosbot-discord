#!/usr/bin/env python3
# Script para adicionar GIF animado no login

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar estilo do GIF antes do .warning
old_warning_style = """        .warning {{
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 50, 0, 0.1);
            border: 2px solid #ff3300;
            color: #ff6666;
            font-size: 14px;
        }}
    </style>"""

new_warning_style = """        .warning {{
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 50, 0, 0.1);
            border: 2px solid #ff3300;
            color: #ff6666;
            font-size: 14px;
        }}
        
        /* GIF animado de fundo */
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
        }}
    </style>"""

content = content.replace(old_warning_style, new_warning_style)

# Adicionar o GIF no body (antes do login-container)
old_body_start = """</head>
<body>
    <div class="login-container">"""

new_body_start = """</head>
<body>
    <!-- GIF animado de fundo -->
    <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDFjZnlmcjdpbjdseTR4ZnU5NWtzOHJhZ3Q0cWp3ZzBrYzFkcWhnbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IeZiGntCfEWOrSjK81/giphy.gif" alt="Animated BG" class="animated-bg">
    
    <div class="login-container">"""

content = content.replace(old_body_start, new_body_start)

# Salvar
with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("GIF animado com efeitos adicionado ao login!")
