#!/bin/bash
# Script automático para configurar servidor de imagens no notebook

echo "===================================="
echo "   SETUP SERVIDOR DE IMAGENS"
echo "===================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Atualizar sistema
echo -e "${YELLOW}[1/6] Atualizando sistema...${NC}"
sudo apt update -qq

# 2. Instalar Python e Git
echo -e "${YELLOW}[2/6] Instalando Python, pip e git...${NC}"
sudo apt install python3 python3-pip python3-venv git wget -y -qq

# 3. Criar pasta
echo -e "${YELLOW}[3/6] Criando pasta ship-server...${NC}"
mkdir -p ~/ship-server
cd ~/ship-server

# 4. Baixar servidor
echo -e "${YELLOW}[4/6] Baixando servidor de imagens...${NC}"
wget -q https://raw.githubusercontent.com/megacavaleiro6662-hub/caosbot-discord/main/image_server.py

# 5. Instalar dependências
echo -e "${YELLOW}[5/6] Instalando Flask, Pillow e Requests...${NC}"
pip3 install flask pillow requests --break-system-packages -q

# 6. Baixar e instalar Ngrok
echo -e "${YELLOW}[6/6] Instalando Ngrok...${NC}"
if [ ! -f /usr/local/bin/ngrok ]; then
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    echo -e "${GREEN}Ngrok instalado!${NC}"
else
    echo -e "${GREEN}Ngrok já instalado!${NC}"
fi

echo ""
echo -e "${GREEN}===================================="
echo "   INSTALAÇÃO COMPLETA!"
echo "====================================${NC}"
echo ""
echo -e "${YELLOW}PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1. Configurar Ngrok:"
echo "   - Crie conta em: https://dashboard.ngrok.com/signup"
echo "   - Pegue seu token em: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "   - Execute: ngrok config add-authtoken SEU_TOKEN"
echo ""
echo "2. Rodar servidor (Terminal 1):"
echo "   cd ~/ship-server"
echo "   python3 image_server.py"
echo ""
echo "3. Expor com Ngrok (Terminal 2):"
echo "   ngrok http 5001"
echo ""
echo "4. Copiar URL do Ngrok (tipo: https://abc123.ngrok.io)"
echo ""
echo "5. Configurar no Render:"
echo "   - Acesse: https://dashboard.render.com"
echo "   - Seu bot > Environment"
echo "   - Add Variable: IMAGE_SERVER_URL = https://abc123.ngrok.io"
echo ""
echo -e "${GREEN}Pronto! Depois é só usar .ship no Discord!${NC}"
