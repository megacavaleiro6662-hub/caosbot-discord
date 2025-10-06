# 🔥 CAOS Hub - Dashboard Web

Dashboard moderno para gerenciar o bot CAOS via interface web.

## ✨ Recursos

### 🎛️ Sistema de Toggle
- **✅ Ligar/Desligar** sistemas com um clique
- **Boas-vindas** - Ative/desative mensagens de entrada
- **Saída/Ban** - Controle mensagens de saída e banimento
- **Autorole** - Sistema de cargo automático
- **Tickets** - Sistema de suporte por tickets

### 📋 Dropdowns Inteligentes
- **SEM digitar IDs** manualmente!
- **Seleção visual** de canais e cargos
- **Multiselect** para cargos de staff
- **Preview** de cores dos cargos

### 🔐 Segurança
- **OAuth2 Discord** para login
- **Verificação de Admin** automática
- **Sessões seguras**

## 🚀 Como Usar

### 1️⃣ Configurar Discord App

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Selecione seu bot
3. Vá em **OAuth2** > **General**
4. Copie o **Client ID** e **Client Secret**
5. Adicione em **Redirects**: `http://localhost:5000/callback`

### 2️⃣ Configurar Variáveis de Ambiente

Crie um arquivo `.env` ou configure no Render:

```env
DISCORD_TOKEN=seu_token_do_bot_aqui
DISCORD_CLIENT_ID=1417623469184516096
DISCORD_CLIENT_SECRET=seu_client_secret_aqui
REDIRECT_URI=http://localhost:5000/callback
DASHBOARD_SECRET=sua_chave_secreta_aqui
```

### 3️⃣ Rodar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar dashboard
python dashboard.py
```

Acesse: `http://localhost:5000`

### 4️⃣ Deploy no Render

**Opção 1: Dashboard Separado**
- Criar novo Web Service no Render
- Conectar repositório
- Build Command: `pip install -r requirements.txt`
- Start Command: `python dashboard.py`

**Opção 2: Junto com o Bot**
- Modificar `caosbot_railway.py` para iniciar Flask em thread
- Usar mesma instância

## 📁 Estrutura de Arquivos

```
github_deploy/
├── dashboard.py              # Aplicação Flask principal
├── templates/
│   ├── index.html           # Página inicial
│   ├── dashboard.html       # Dashboard principal
│   └── tickets.html         # Configuração de tickets
├── static/
│   └── style.css            # Estilos modernos
├── ticket_config.json       # Configurações salvas (auto-criado)
└── welcome_config.json      # Configurações de eventos (auto-criado)
```

## 🎫 Configurar Tickets

1. **Login** no dashboard
2. Clique em **🎫 Tickets** no menu
3. **Selecione:**
   - 📂 Categoria onde tickets serão criados
   - 👮 Cargos que terão acesso aos tickets
   - 💬 Mensagem de boas-vindas personalizada
4. **Ative** o toggle
5. **Salve** as configurações

## 🎨 Screenshots

### Página Inicial
![Login](https://via.placeholder.com/800x400?text=Login+Page)

### Dashboard Principal
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Main)

### Configuração de Tickets
![Tickets](https://via.placeholder.com/800x400?text=Ticket+Config)

## 🛠️ Tecnologias

- **Flask** - Framework web
- **Discord OAuth2** - Autenticação
- **Discord API** - Buscar dados do servidor
- **JavaScript** - Interatividade
- **CSS3** - Design moderno

## ⚡ API Endpoints

### GET `/dashboard`
Dashboard principal com status dos sistemas

### GET `/dashboard/tickets`
Página de configuração de tickets

### POST `/api/tickets/save`
Salva configurações de tickets
```json
{
  "enabled": true,
  "category_id": "1234567890",
  "staff_role_ids": ["123", "456"],
  "welcome_message": "Olá! Como podemos ajudar?"
}
```

### POST `/api/toggle/<system>`
Liga/desliga sistemas (welcome, goodbye, autorole, tickets)

## 🐛 Troubleshooting

### Erro: "Client Secret inválido"
- Verifique se copiou o Client Secret correto
- Gere um novo no Discord Developer Portal

### Erro: "Não é administrador"
- Certifique-se de ter permissão de **ADMINISTRADOR** no servidor
- ID do servidor está correto no código (GUILD_ID)

### Erro: "Bot token inválido"
- Verifique a variável `DISCORD_TOKEN`
- Token deve ser do bot, não do usuário

## 📝 Notas

- **Permissões:** Apenas administradores podem acessar
- **Servidor:** Configurado para o servidor CAOS Hub (ID: 1365510151884378214)
- **Multi-servidor:** Para usar em múltiplos servidores, modificar lógica do GUILD_ID

## 🔥 Criado por

**CAOS Hub Team**
- Discord Bot + Dashboard Web
- Sistema completo de moderação e tickets
- Interface moderna e intuitiva

---

**Versão:** 2.0  
**Última atualização:** Janeiro 2025
