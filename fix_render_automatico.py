#!/usr/bin/env python3
"""
Script para criar Web Service automaticamente no Render
Usa a API do Render para automatizar todo o processo
"""

import requests
import json
import os
import sys

print("=" * 60)
print("🔧 AUTOMAÇÃO RENDER - WEB SERVICE")
print("=" * 60)

# Solicitar API Key
print("\n📍 PASSO 1: Preciso da sua API Key do Render")
print("   Como pegar:")
print("   1. Acesse: https://dashboard.render.com/account/settings")
print("   2. Vai em 'API Keys'")
print("   3. Clica em 'Create API Key'")
print("   4. Copia a key")
print()

api_key = input("Cole sua API Key aqui: ").strip()

if not api_key:
    print("❌ API Key não fornecida!")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("\n✅ API Key configurada!")
print("\n📍 PASSO 2: Criando novo Web Service...")

# Dados do novo serviço
service_data = {
    "type": "web_service",
    "name": "caosbot-discord-web",
    "repo": "https://github.com/megacavaleiro6662-hub/caosbot-discord",
    "branch": "main",
    "runtime": "python",
    "buildCommand": "",
    "startCommand": "python caosbot_railway.py",
    "envVars": [
        {
            "key": "DISCORD_TOKEN",
            "value": input("\n🔑 DISCORD_TOKEN: ").strip()
        },
        {
            "key": "DISCORD_CLIENT_ID",
            "value": input("🔑 DISCORD_CLIENT_ID: ").strip()
        },
        {
            "key": "DISCORD_CLIENT_SECRET",
            "value": input("🔑 DISCORD_CLIENT_SECRET: ").strip()
        },
        {
            "key": "DISCORD_SERVER_ID",
            "value": input("🔑 DISCORD_SERVER_ID: ").strip()
        },
        {
            "key": "PORT",
            "value": "10000"
        }
    ],
    "serviceDetails": {
        "plan": "free"
    }
}

print("\n📍 PASSO 3: Gerando REDIRECT_URI...")
print("   Formato: https://caosbot-discord-web.onrender.com/callback")

redirect_uri = input("\nConfirma essa URL? (s/n): ").strip().lower()
if redirect_uri == 's':
    service_data["envVars"].append({
        "key": "DISCORD_REDIRECT_URI",
        "value": "https://caosbot-discord-web.onrender.com/callback"
    })
else:
    custom_uri = input("Cole a URL customizada: ").strip()
    service_data["envVars"].append({
        "key": "DISCORD_REDIRECT_URI",
        "value": custom_uri
    })

print("\n🚀 Criando serviço no Render...")
print("   Aguarde...")

try:
    response = requests.post(
        'https://api.render.com/v1/services',
        headers=headers,
        json=service_data
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("\n✅ SUCESSO! Web Service criado!")
        print(f"\n📍 URL do Dashboard: {result.get('serviceDetails', {}).get('url', 'URL será gerada em breve')}")
        print(f"📍 ID do Serviço: {result.get('id')}")
        print("\n⏰ Aguarde 5-10 minutos para o deploy completar!")
        print("\n📝 IMPORTANTE:")
        print("   1. Acesse o Discord Developers")
        print("   2. Adicione a URL do callback nos Redirects:")
        print(f"      {service_data['envVars'][-1]['value']}")
    else:
        print(f"\n❌ ERRO: {response.status_code}")
        print(f"Resposta: {response.text}")
        print("\n💡 Possíveis problemas:")
        print("   - API Key inválida")
        print("   - Repositório não encontrado")
        print("   - Nome do serviço já existe")
        
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\n💡 Tente criar manualmente seguindo o guia")

print("\n" + "=" * 60)
print("Script finalizado!")
print("=" * 60)
