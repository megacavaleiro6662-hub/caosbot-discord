from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import requests
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            # Extrair dados do ranking (esperado como JSON)
            ranking_data = json.loads(params.get('data', ['[]'])[0])
            server_name = params.get('server', ['CAOS HUB'])[0]
            
            if not ranking_data:
                self.send_error(400, "No ranking data provided")
                return
            
            # Criar imagem do leaderboard
            img = self.create_leaderboard_image(ranking_data, server_name)
            
            # Converter para bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Enviar resposta
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'public, max-age=300')
            self.end_headers()
            self.wfile.write(img_bytes.read())
            
        except Exception as e:
            self.send_error(500, f"Error generating image: {str(e)}")
    
    def create_leaderboard_image(self, ranking_data, server_name):
        # Dimensões
        width = 1000
        height = 100 + (len(ranking_data) * 90) + 80  # Header + entries + footer
        
        # Criar imagem com gradiente laranja
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        # Gradiente laranja CAOS (fundo)
        for y in range(height):
            r = int(255 * (1 - y/height * 0.3))
            g = int(100 * (1 - y/height * 0.5))
            b = int(0)
            draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        
        # Overlay semi-transparente para legibilidade
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Tentar usar fonte (fallback se não existir)
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_name = ImageFont.truetype("arial.ttf", 32)
            font_stats = ImageFont.truetype("arial.ttf", 24)
            font_footer = ImageFont.truetype("arial.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()
            font_stats = ImageFont.load_default()
            font_footer = ImageFont.load_default()
        
        # Header
        title = f"🏆 RANKING XP - {server_name.upper()}"
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) / 2, 20), title, fill='#FFFFFF', font=font_title)
        
        # Linha decorativa
        draw.rectangle([(50, 85), (width - 50, 88)], fill='#FF6600')
        
        # Desenhar cada entrada do ranking
        y_offset = 110
        medals = ['🥇', '🥈', '🥉']
        
        for i, entry in enumerate(ranking_data[:10]):
            username = entry.get('username', 'Unknown')
            level = entry.get('level', 0)
            xp = entry.get('xp', 0)
            avatar_url = entry.get('avatar', '')
            
            # Medal ou posição
            position = medals[i] if i < 3 else f"#{i+1:02d}"
            
            # Desenhar fundo da entrada
            entry_bg = Image.new('RGBA', (900, 70), (30, 30, 30, 200))
            img.paste(entry_bg, (50, y_offset), entry_bg)
            
            # Avatar
            if avatar_url:
                try:
                    avatar_response = requests.get(avatar_url, timeout=3)
                    avatar = Image.open(BytesIO(avatar_response.content))
                    avatar = avatar.resize((60, 60))
                    
                    # Fazer avatar circular
                    mask = Image.new('L', (60, 60), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, 60, 60), fill=255)
                    
                    img.paste(avatar, (70, y_offset + 5), mask)
                except:
                    pass
            
            # Posição/Medal
            draw.text((140, y_offset + 5), position, fill='#FFD700', font=font_name)
            
            # Nome
            draw.text((200, y_offset + 5), username[:20], fill='#FFFFFF', font=font_name)
            
            # Level
            draw.text((550, y_offset + 5), f"Lv.{level:02d}", fill='#FF6600', font=font_stats)
            
            # XP
            xp_text = f"{xp:,} XP".replace(',', '.')
            draw.text((650, y_offset + 5), xp_text, fill='#CCCCCC', font=font_stats)
            
            # Barra de progresso
            if ranking_data:
                max_xp = max(e.get('xp', 1) for e in ranking_data)
                bar_width = int((xp / max(max_xp, 1)) * 200)
                draw.rectangle([(140, y_offset + 50), (140 + 200, y_offset + 60)], fill='#333333')
                draw.rectangle([(140, y_offset + 50), (140 + bar_width, y_offset + 60)], fill='#FF6600')
            
            y_offset += 90
        
        # Footer
        footer_text = "🔥 CAOS HUB • Sistema de XP tipo Loritta"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((width - footer_width) / 2, height - 50), footer_text, fill='#AAAAAA', font=font_footer)
        
        return img
