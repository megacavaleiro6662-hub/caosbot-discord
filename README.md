# 🤖 CAOS Bot - Sistema Completo com Wavelink

Bot Discord completo com sistema de moderação, tickets, boas-vindas e **sistema de música profissional usando Wavelink/Lavalink**.

## 🚀 Deploy no Render (100% Gratuito)

### 📦 Arquivos Incluídos:

- `caosbot_railway.py` - Bot principal com Wavelink integrado
- `Dockerfile` - Container com Python + Java
- `start.sh` - Script que inicia Lavalink e Bot juntos
- `application.yml` - Configuração do Lavalink
- `requirements.txt` - Dependências Python
- `Procfile` - (Opcional, não usado com Docker)

---

## 🔧 Como Fazer Deploy:

### 1. Criar Web Service no Render

1. Acesse: https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Conecte a este repositório

### 2. Configurações:

```
Name: caosbot-completo
Region: Oregon (US West)
Branch: main
Runtime: Docker              ← IMPORTANTE!
Dockerfile Path: ./Dockerfile
Instance Type: Free
```

### 3. Variáveis de Ambiente:

```
DISCORD_TOKEN=seu_token_principal
MUSIC_TOKEN_1=token_music_bot_1
MUSIC_TOKEN_2=token_music_bot_2 (opcional)
MUSIC_TOKEN_3=token_music_bot_3 (opcional)
MUSIC_TOKEN_4=token_music_bot_4 (opcional)
PORT=10000
```

### 4. Deploy

- Clique em **"Create Web Service"**
- Aguarde 10-15 minutos (instala Java + Python)

---

## 🎵 Sistema de Música

### Comandos:

- `mc.p <música>` - Tocar música
- `mc.skip` - Pular música (votação 60%)
- `mc.stop` - Parar música
- `mc.pause` / `mc.resume` - Pausar/retomar
- `mc.queue` - Ver fila
- `mc.vol <0-100>` - Ajustar volume
- `mc.shuffle` - Embaralhar fila
- `mc.leave` - Sair do canal

### Recursos:

✅ Sistema profissional com Wavelink/Lavalink
✅ Pool de 4 bots de música
✅ Painel interativo com botões
✅ Sistema de votação para skip
✅ Loop de música/fila
✅ Busca por nome ou link

---

## 🛡️ Sistema de Moderação

- Sistema completo de advertências (ADV 1, 2, 3)
- Logs detalhados de moderação
- Sistema de tickets
- Boas-vindas/saída/ban automáticos
- Autorole
- Bloqueio de bots em calls específicas

---

## 📊 Logs Esperados:

```
🚀 Iniciando sistema de música CAOS...
🎵 Iniciando servidor Lavalink...
✅ Lavalink iniciado com sucesso
✅ Conectado ao Lavalink: http://127.0.0.1:2333
🤖 Iniciando bot Discord...
✅ Bot pronto! Sistema anti-hibernação ATIVADO!
```

---

## 💰 Custo:

- **100% GRATUITO** no Render Free Tier (750h/mês)
- 1 serviço apenas (Bot + Lavalink no mesmo container)

---

## 🆘 Problemas?

### Erro: "Failed to connect to Lavalink"
- Aguarde 30-45 segundos após o deploy
- Lavalink demora para inicializar

### Build falha
- Verifique se todos os arquivos estão no repositório
- Confirme que Runtime está como "Docker"

---

## 📝 Notas:

- Lavalink roda **localmente** no mesmo container (localhost:2333)
- Não precisa de servidor Lavalink separado
- Sistema anti-hibernação incluído
- Compatível com Render Free Tier

---

**Desenvolvido por:** megacavaleiro6662-hub
**Plataforma:** Render.com
**Tecnologias:** Python, Discord.py, Wavelink, Lavalink, Docker
