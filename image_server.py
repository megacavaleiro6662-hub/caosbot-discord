#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIDOR DE IMAGENS DE SHIP
Roda no notebook para gerar imagens que o bot no Render usa
"""

from flask import Flask, send_file, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Verificar se servidor está online"""
    return jsonify({"status": "online", "message": "Servidor de imagens funcionando!"})

@app.route('/ship', methods=['GET'])
def generate_ship():
    """Gera imagem de ship"""
    try:
        # Pegar parâmetros
        avatar1_url = request.args.get('avatar1')
        avatar2_url = request.args.get('avatar2')
        percentage = int(request.args.get('percentage', 50))
        ship_name = request.args.get('name', 'SHIP')
        
        if not avatar1_url or not avatar2_url:
            return jsonify({"error": "Faltam parâmetros!"}), 400
        
        # Tamanho da imagem
        width, height = 800, 400
        
        # Cor de fundo baseada na porcentagem
        if percentage >= 75:
            bg_color = (40, 15, 25)  # Rosa escuro
        elif percentage >= 50:
            bg_color = (40, 30, 10)  # Dourado escuro
        else:
            bg_color = (20, 20, 25)  # Cinza escuro
        
        # Criar imagem
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Baixar avatares
        try:
            response1 = requests.get(avatar1_url, timeout=10)
            avatar1 = Image.open(BytesIO(response1.content)).convert('RGBA').resize((150, 150))
            
            response2 = requests.get(avatar2_url, timeout=10)
            avatar2 = Image.open(BytesIO(response2.content)).convert('RGBA').resize((150, 150))
        except Exception as e:
            print(f"Erro ao baixar avatares: {e}")
            return jsonify({"error": "Erro ao baixar avatares"}), 500
        
        # Criar máscaras circulares
        mask = Image.new('L', (150, 150), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 150, 150), fill=255)
        
        # Aplicar máscaras
        avatar1.putalpha(mask)
        avatar2.putalpha(mask)
        
        # Colar avatares
        img.paste(avatar1, (80, 125), avatar1)
        img.paste(avatar2, (570, 125), avatar2)
        
        # Desenhar coração no meio
        heart_x, heart_y = 360, 150
        heart_color = (255, 50, 100) if percentage >= 50 else (100, 100, 100)
        
        # Coração
        draw.ellipse([heart_x, heart_y, heart_x+30, heart_y+30], fill=heart_color)
        draw.ellipse([heart_x+20, heart_y, heart_x+50, heart_y+30], fill=heart_color)
        draw.polygon([
            (heart_x+5, heart_y+25),
            (heart_x+45, heart_y+25),
            (heart_x+25, heart_y+55)
        ], fill=heart_color)
        
        # Tentar carregar fonte
        try:
            font_large = ImageFont.truetype("arial.ttf", 40)
            font_medium = ImageFont.truetype("arial.ttf", 30)
        except:
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
        
        # Título (nome do ship)
        title_text = ship_name.upper()
        draw.text((width//2, 40), title_text, fill=(255, 255, 255), font=font_large, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Porcentagem
        percent_text = f"{percentage}%"
        draw.text((width//2, 190), percent_text, fill=(255, 200, 0), font=font_large, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Barra de progresso
        bar_x, bar_y = 150, 320
        bar_width, bar_height = 500, 40
        
        # Fundo da barra
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_width, bar_y+bar_height], radius=20, fill=(50, 50, 50))
        
        # Barra preenchida
        filled_width = int(bar_width * (percentage / 100))
        if filled_width > 0:
            fill_color = (255, 50, 100) if percentage >= 50 else (100, 100, 100)
            draw.rounded_rectangle([bar_x, bar_y, bar_x+filled_width, bar_y+bar_height], radius=20, fill=fill_color)
        
        # Salvar em BytesIO
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        print(f"✅ Imagem gerada: {ship_name} - {percentage}%")
        
        return send_file(output, mimetype='image/png')
    
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎨 Servidor de Imagens INICIADO!")
    print("📡 Aguardando requisições...")
    print("🌐 Rode ngrok para expor: ngrok http 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
