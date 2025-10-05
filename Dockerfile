FROM python:3.11-slim

# Instalar dependências básicas
RUN apt-get update && apt-get install -y \
    ffmpeg curl procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar arquivos da aplicação
COPY caosbot_railway.py /app/
COPY start.sh /app/
COPY requirements.txt /app/

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Dar permissão de execução
RUN chmod +x /app/start.sh

EXPOSE 10000

CMD ["bash", "/app/start.sh"]