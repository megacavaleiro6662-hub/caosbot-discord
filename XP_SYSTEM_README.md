# 🎮 **SISTEMA DE XP COMPLETO - DOCUMENTAÇÃO**

## ✅ **O QUE FOI IMPLEMENTADO:**

### **📂 Arquivos Criados:**

1. **`xp_database.py`** - Banco de dados SQLAlchemy
   - Tabelas: `xp_users`, `xp_config`, `xp_levels`, `xp_boosts`, `xp_logs`
   - Funções CRUD completas
   - Suporte PostgreSQL/SQLite

2. **`xp_system.py`** - Sistema automático de XP
   - Ganho de XP por mensagem
   - Cooldown configurável
   - Anti-spam
   - Multiplicadores por cargo
   - Cache em memória
   - Level up automático

3. **`image_generator.py`** - Gerador de rank cards (Pillow)
   - Rank card 800x250px
   - Avatar circular
   - Barra de progresso
   - Level up card
   - Leaderboard image

4. **`xp_commands.py`** - Comandos Discord
   - `.xp [@usuário]` - Mostra rank card
   - `.xprank [quantidade]` - Top 10 em imagem
   - `.xpreset @usuário` - Reseta XP (admin)
   - `.xpresetall` - Reseta todos (admin)
   - `.xpboost [mult] [min]` - Ativa boost
   - `.xpconfig` - Mostra configuração
   - `.xpsetup` - Inicializa sistema

5. **`xp_dashboard.py`** - Dashboard web FastAPI
   - OAuth Discord
   - APIs REST completas
   - Rotas para todas as configurações
   - Exportação CSV
   - Leaderboard público

6. **Templates HTML:**
   - `base.html` - Layout base
   - `index.html` - Login
   - `servers.html` - Lista de servidores
   - `leaderboard_public.html` - Ranking público

7. **`static/js/xp_dashboard.js`** - JavaScript
   - Preview de mensagens em tempo real
   - Chamadas de API
   - Interatividade completa

---

## 🚀 **COMO USAR:**

### **1️⃣ APÓS O DEPLOY:**

O sistema já está **100% integrado** no `caosbot_railway.py`! 

**O que acontece automaticamente:**
- ✅ Bot inicia normalmente
- ✅ Sistema de XP carrega automaticamente
- ✅ Níveis padrão são criados para cada servidor
- ✅ Dashboard FastAPI roda na porta 8000
- ✅ Flask continua na porta principal (10000)

---

### **2️⃣ ACESSAR O DASHBOARD:**

#### **No Render:**
```
https://seu-app.onrender.com:8000
```

#### **Local:**
```
http://localhost:8000
```

**Login:** Usa o mesmo OAuth Discord já configurado!

---

### **3️⃣ COMANDOS DISCORD:**

```bash
.xpsetup              # Cria os 8 níveis padrão
.xp                   # Seu rank card
.xp @usuário          # Rank card de alguém
.xprank               # Top 10 do servidor
.xpconfig             # Ver configuração atual
.xpboost 2.0 60       # 2x XP por 60 minutos (admin)
.xpreset @user        # Resetar XP de alguém (admin)
.xpresetall           # Resetar todos (admin, confirmação dupla)
```

---

### **4️⃣ NÍVEIS PADRÃO:**

| Nível | Nome          | XP Necessário | Multiplicador |
|-------|---------------|---------------|---------------|
| 1     | noob          | 0             | 1.0x          |
| 2     | bacon hair    | 200           | 1.0x          |
| 3     | pro           | 500           | 1.0x          |
| 4     | try harder    | 1,000         | **2.0x**      |
| 5     | épico         | 2,000         | **1.5x**      |
| 6     | místico       | 4,000         | **1.5x**      |
| 7     | lendário      | 8,000         | **2.0x**      |
| 8     | gilipado      | 16,000        | **3.0x**      |

**IDs dos cargos estão no código!** Configure no dashboard se precisar mudar.

---

## ⚙️ **FUNCIONALIDADES DO DASHBOARD:**

### **📄 Página 1: Geral**
- Toggle ON/OFF sistema
- Intervalo de XP (min-max)
- Cooldown global (segundos)
- Canal de log
- Botão "Zerar XP de todos"

### **📄 Página 2: Níveis**
- Lista de todos os níveis
- Editar: Nome, ID do cargo, XP necessário, Multiplicador
- Adicionar/Remover níveis

### **📄 Página 3: Recompensas**
- Modo: Empilhar OU Substituir cargos
- XP bônus ao subir de nível

### **📄 Página 4: Bloqueios**
- Cargos que não ganham XP
- Canais bloqueados

### **📄 Página 5: Mensagens** ⭐
- Tipo de anúncio: Nenhum / Canal atual / DM / Canal personalizado
- Tipo de mensagem: Texto / Embed / Imagem
- Editor com placeholders
- **Preview em tempo real!**

### **📄 Página 6: Rank Card** 🎨
- Cor de fundo
- Imagem de fundo (URL)
- Cor da barra
- Cor do texto

### **📄 Página 7: Estatísticas** 📊
- Total de usuários com XP
- XP total do servidor
- Média de XP
- Total de mensagens
- Logs recentes
- Exportar CSV

### **📄 Página 8: Boosts** 🚀
- Criar boost temporário
- Ver boosts ativos

---

## 🔧 **VARIÁVEIS DE AMBIENTE (JÁ CONFIGURADAS!):**

O sistema **REUTILIZA** as variáveis que você já tem no Render:

```bash
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_client_secret
DISCORD_REDIRECT_URI=https://seu-app.onrender.com/callback
SECRET_KEY=qualquer_string_aleatoria
DISCORD_TOKEN=seu_bot_token
```

**NÃO PRECISA ADICIONAR NADA NOVO!** ✅

---

## 📦 **DEPENDÊNCIAS (requirements.txt):**

Já foram adicionadas:
```
SQLAlchemy==2.0.23
Pillow==10.1.0
fastapi==0.104.1
uvicorn==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
itsdangerous==2.1.2
```

---

## 🗃️ **BANCO DE DADOS:**

O sistema usa **SQLite** por padrão (`xp_system.db`).

**Para usar PostgreSQL no Render:**
1. Adicione `DATABASE_URL` nas variáveis de ambiente
2. O sistema detecta automaticamente!

---

## 🎯 **PLACEHOLDERS DISPONÍVEIS:**

Use nas mensagens de level up:

- `{user}` - Nome do usuário
- `{user_mention}` - @Menção do usuário
- `{level}` - Nível alcançado
- `{level_name}` - Nome do cargo
- `{xp}` - XP total
- `{next_level_xp}` - XP do próximo nível
- `{guild_name}` - Nome do servidor

**Exemplo:**
```
🎉 {user_mention} subiu para o nível **{level}** ({level_name})! 
Próximo nível em: **{next_level_xp} XP**
```

---

## 🔗 **LEADERBOARD PÚBLICO:**

Acesse sem login:
```
https://seu-app.onrender.com:8000/leaderboard/SEU_GUILD_ID
```

**Mostra top 100 usuários!**

---

## 🐛 **TROUBLESHOOTING:**

### **"Sistema de XP não disponível"**
- Verifique se todos os arquivos foram commitados
- Rode: `pip install -r requirements.txt`

### **"Erro ao gerar rank card"**
- Pillow precisa de fontes do sistema
- O bot tem fallback para embed se Pillow falhar

### **Dashboard não abre**
- Verifique se a porta 8000 está aberta no Render
- Logs: `RuntimeError` geralmente é porta já em uso

### **XP não está sendo ganho**
- Use `.xpsetup` para criar os níveis
- Verifique se o sistema está ativado no dashboard
- Confira cooldown e canais bloqueados

---

## 📈 **PERFORMANCE:**

- ✅ Cache em memória para reduzir queries
- ✅ Sincronização automática a cada 5 minutos
- ✅ Async/await em todas operações
- ✅ Threads separadas (Bot + Flask + FastAPI)

---

## 🎉 **TUDO PRONTO!**

**Apenas faça:**
```bash
git add .
git commit -m "Sistema de XP completo integrado!"
git push origin main
```

**O Render vai:**
1. Instalar dependências
2. Iniciar bot Discord
3. Iniciar Flask (porta 10000)
4. Iniciar Dashboard XP (porta 8000)

**TUDO AUTOMÁTICO! 🚀💯**

---

## 💬 **SUPORTE:**

- **Dashboard Principal:** `https://seu-app.onrender.com`
- **Dashboard XP:** `https://seu-app.onrender.com:8000`
- **Comandos:** `.help` no Discord

---

**SISTEMA 100% FUNCIONAL E PRONTO PARA USO! 🎮✨**
