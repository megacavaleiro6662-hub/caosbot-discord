# 🎛️ CAOS BOT - DASHBOARD

Dashboard web para controle do bot Discord em tempo real.

## 🚀 Como Usar

### 1️⃣ Rodar Localmente
```bash
python dashboard.py
```
Acesse: http://localhost:5000

### 2️⃣ Deploy no Render/Heroku
O dashboard pode rodar separadamente ou junto com o bot.

**Variáveis de ambiente:**
- `PORT` - Porta do servidor (padrão: 5000)

## 📋 Funcionalidades

- ✅ **Toggle em tempo real** - Ativa/desativa sistemas instantaneamente
- 🔄 **Auto-sync** - Bot sincroniza a cada 3 segundos
- 📊 **Status ao vivo** - Visualização do estado atual
- 💾 **Salva automaticamente** - Todas as mudanças são persistidas

## 🎯 Sistemas Controlados

1. **👋 Boas-vindas** - Mensagens de entrada
2. **👋 Saída/Ban** - Mensagens de saída e banimento
3. **🎭 Autorole** - Cargo automático para novos membros
4. **🎫 Tickets** - Sistema de tickets de suporte

## 🔗 API Endpoints

### GET `/api/config/status`
Retorna configurações atuais
```json
{
  "welcome_enabled": true,
  "goodbye_enabled": false,
  "autorole_enabled": true,
  "tickets_enabled": false
}
```

### POST `/api/config/toggle`
Alterna uma configuração
```json
{
  "key": "welcome_enabled"
}
```

### POST `/api/config/update`
Atualiza múltiplas configs
```json
{
  "welcome_enabled": true,
  "goodbye_enabled": true,
  "autorole_enabled": false,
  "tickets_enabled": true
}
```

## 📁 Estrutura

```
dashboard.py          # Servidor Flask principal
templates/
  └── dashboard.html  # Interface web
static/
  └── style.css      # Estilização
welcome_config.json  # Configs salvas (gerado automaticamente)
```

## 🎨 Design

- **Responsivo** - Funciona em mobile e desktop
- **Moderno** - Design com gradientes e animações
- **Intuitivo** - Toggle switches e notificações visuais

## 🔧 Integração com o Bot

O bot verifica o arquivo `welcome_config.json` a cada 3 segundos e aplica as mudanças automaticamente. Não precisa reiniciar!

## 📝 Notas

- As configurações são salvas em `welcome_config.json`
- O bot precisa ter acesso ao mesmo arquivo
- Mudanças são aplicadas em até 3 segundos
