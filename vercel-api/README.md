# 🎨 CAOS Bot - Leaderboard Card API

API serverless para gerar imagens customizadas de leaderboard/ranking para o CAOS Bot.

## 🚀 Features

- ✅ Geração de imagens PNG customizadas
- ✅ Fundo gradiente laranja CAOS
- ✅ TOP 10 com avatares dos usuários
- ✅ Barras de progresso visuais
- ✅ Medalhas para TOP 3 (🥇🥈🥉)
- ✅ 100% grátis no Vercel

## 📦 Deploy

1. Crie conta no [Vercel](https://vercel.com)
2. Conecte o repositório caosbot-discord
3. Configure: Root Directory = `vercel-api`
4. Deploy automático!

## 🔧 Como usar

```
GET /api/leaderboard?data=<JSON>&server=<NOME>
```

### Parâmetros:

- `data`: JSON array com dados do ranking
- `server`: Nome do servidor (opcional)

### Exemplo de data:

```json
[
  {
    "username": "João",
    "level": 25,
    "xp": 15811,
    "avatar": "https://cdn.discordapp.com/avatars/..."
  },
  {
    "username": "Maria",
    "level": 20,
    "xp": 8944,
    "avatar": "https://cdn.discordapp.com/avatars/..."
  }
]
```

## 🎨 Output

Retorna uma imagem PNG (1000x altura variável) com:
- Header com título do servidor
- TOP 10 usuários com avatares
- Barras de progresso
- Footer do CAOS Hub

## 📝 License

MIT - CAOS Hub 2025
