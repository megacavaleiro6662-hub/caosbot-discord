#!/bin/bash
# Script que FAZ TUDO de uma vez - instalação + configuração + execução

clear
echo "═══════════════════════════════════════════════════"
echo "      SETUP COMPLETO - SERVIDOR DE IMAGENS        "
echo "═══════════════════════════════════════════════════"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar se é root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Não rode como root! Use um usuário normal.${NC}"
    exit 1
fi

# Pedir token do Ngrok
echo -e "${YELLOW}PASSO 1: TOKEN DO NGROK${NC}"
echo ""
echo "1. Acesse: https://dashboard.ngrok.com/signup"
echo "2. Crie uma conta (ou faça login)"
echo "3. Copie seu token em: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
read -p "Cole seu token do Ngrok aqui: " NGROK_TOKEN

if [ -z "$NGROK_TOKEN" ]; then
    echo -e "${RED}Token vazio! Abortando.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Token recebido! Começando instalação...${NC}"
echo ""

# Atualizar sistema
echo -e "${BLUE}[1/7] Atualizando sistema...${NC}"
sudo apt update -qq
sudo apt upgrade -y -qq

# Instalar dependências
echo -e "${BLUE}[2/7] Instalando Python, pip, git...${NC}"
sudo apt install python3 python3-pip python3-venv git wget curl -y -qq

# Criar pasta
echo -e "${BLUE}[3/7] Criando estrutura de pastas...${NC}"
mkdir -p ~/ship-server
cd ~/ship-server

# Baixar servidor
echo -e "${BLUE}[4/7] Baixando servidor de imagens...${NC}"
wget -q https://raw.githubusercontent.com/megacavaleiro6662-hub/caosbot-discord/main/image_server.py

# Instalar bibliotecas Python
echo -e "${BLUE}[5/7] Instalando Flask, Pillow, Requests...${NC}"
pip3 install flask pillow requests --break-system-packages -q

# Instalar e configurar Ngrok
echo -e "${BLUE}[6/7] Instalando e configurando Ngrok...${NC}"
if [ ! -f /usr/local/bin/ngrok ]; then
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
fi

# Configurar token
ngrok config add-authtoken $NGROK_TOKEN > /dev/null 2>&1

# Criar script de inicialização
echo -e "${BLUE}[7/7] Criando script de inicialização...${NC}"
cat > ~/ship-server/start.sh << 'EOF'
#!/bin/bash
# Script para iniciar servidor + ngrok

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd ~/ship-server

echo "═══════════════════════════════════════════════════"
echo "      INICIANDO SERVIDOR DE IMAGENS        "
echo "═══════════════════════════════════════════════════"
echo ""

# Matar processos antigos se existirem
pkill -f image_server.py > /dev/null 2>&1
pkill -f ngrok > /dev/null 2>&1

# Iniciar servidor em background
echo -e "${BLUE}Iniciando servidor Flask...${NC}"
python3 image_server.py > server.log 2>&1 &
SERVER_PID=$!

# Aguardar servidor iniciar
sleep 3

# Iniciar ngrok em background
echo -e "${BLUE}Iniciando Ngrok...${NC}"
ngrok http 5001 > /dev/null 2>&1 &
NGROK_PID=$!

# Aguardar ngrok iniciar
sleep 3

# Pegar URL do ngrok
echo -e "${BLUE}Obtendo URL pública...${NC}"
sleep 2

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -n 1)

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}Erro ao obter URL do Ngrok!${NC}"
    echo "Verifique se o ngrok está rodando: http://localhost:4040"
    exit 1
fi

clear
echo "═══════════════════════════════════════════════════"
echo "      ✅ SERVIDOR INICIADO COM SUCESSO!        "
echo "═══════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}📡 Servidor rodando em: http://localhost:5001${NC}"
echo -e "${GREEN}🌐 URL Pública: $NGROK_URL${NC}"
echo ""
echo "═══════════════════════════════════════════════════"
echo "      CONFIGURAR NO RENDER AGORA:        "
echo "═══════════════════════════════════════════════════"
echo ""
echo "1. Acesse: https://dashboard.render.com"
echo "2. Clique no seu bot: caosbot-discord"
echo "3. Vá em: Environment"
echo "4. Clique em: Add Environment Variable"
echo "5. Adicione:"
echo ""
echo -e "   ${YELLOW}Nome:${NC}  IMAGE_SERVER_URL"
echo -e "   ${YELLOW}Valor:${NC} $NGROK_URL"
echo ""
echo "6. Clique em Save Changes"
echo ""
echo "═══════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Depois use .ship no Discord e vai ter imagem! 🎨${NC}"
echo ""
echo "Para parar o servidor: pkill -f image_server && pkill -f ngrok"
echo "Para ver logs: tail -f ~/ship-server/server.log"
echo ""
echo "Deixe este terminal aberto para manter o servidor rodando!"
echo ""

# Manter script rodando
wait
EOF

chmod +x ~/ship-server/start.sh

clear
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════"
echo "      ✅ INSTALAÇÃO COMPLETA!        "
echo "═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}AGORA RODE O COMANDO ABAIXO PARA INICIAR TUDO:${NC}"
echo ""
echo -e "${BLUE}    ~/ship-server/start.sh${NC}"
echo ""
echo "═══════════════════════════════════════════════════"
