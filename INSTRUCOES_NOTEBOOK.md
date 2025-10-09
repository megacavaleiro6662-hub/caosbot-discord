# 🎨 INSTRUÇÕES PARA SERVIDOR DE IMAGENS NO NOTEBOOK

## 📋 O QUE VOCÊ VAI FAZER:

1. Instalar Python, Git e Ngrok no notebook
2. Baixar o servidor de imagens
3. Rodar o servidor
4. Expor pra internet com Ngrok
5. Configurar o bot no Render pra usar

---

## 🚀 PASSO A PASSO:

### 1️⃣ INSTALAR NO NOTEBOOK (LINUX):

```bash
# Atualizar sistema
sudo apt update

# Instalar Python, pip e git
sudo apt install python3 python3-pip git -y

# Instalar bibliotecas
pip3 install flask pillow requests
```

### 2️⃣ BAIXAR O SERVIDOR:

```bash
# Criar pasta
mkdir ship-server
cd ship-server

# Baixar só o arquivo do servidor
wget https://raw.githubusercontent.com/megacavaleiro6662-hub/caosbot-discord/main/image_server.py
```

### 3️⃣ INSTALAR NGROK:

```bash
# Baixar ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extrair
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Mover para pasta do sistema
sudo mv ngrok /usr/local/bin/
```

### 4️⃣ CONFIGURAR NGROK:

1. Crie conta em: https://dashboard.ngrok.com/signup
2. Pegue seu token em: https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure:

```bash
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### 5️⃣ RODAR O SERVIDOR:

**Terminal 1 - Servidor:**
```bash
python3 image_server.py
```

Deve aparecer:
```
🎨 Servidor de Imagens INICIADO!
📡 Aguardando requisições...
```

**Terminal 2 - Ngrok:**
```bash
ngrok http 5001
```

Vai aparecer algo assim:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5001
```

**COPIA ESSA URL!** (exemplo: `https://abc123.ngrok.io`)

### 6️⃣ CONFIGURAR NO RENDER:

1. Entra em: https://dashboard.render.com
2. Clica no **caosbot-discord**
3. Vai em **Environment**
4. Clica em **Add Environment Variable**
5. Nome: `IMAGE_SERVER_URL`
6. Valor: `https://abc123.ngrok.io` (a URL que você copiou)
7. Clica em **Save Changes**

O bot vai **redeployar automaticamente**!

---

## ✅ TESTAR:

Depois que redeployar, usa `.ship @user1 @user2` no Discord!

Se funcionar, vai aparecer a **IMAGEM LINDA** com os avatares! 🎨

---

## ⚠️ IMPORTANTE:

- Notebook precisa ficar **LIGADO** pra funcionar
- Se desligar, volta a ser **sem imagem**
- Ngrok muda a URL se reiniciar (versão free)
- Pra URL fixa, precisa pagar Ngrok ($8/mês)

---

## 🔥 PRONTO!

Agora o bot no Render usa o notebook pra gerar imagens! 💯
