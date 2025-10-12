#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cria Web Service automaticamente no Render
"""

import requests
import json
import sys
import io

# Fix encoding no Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = "rnd_iCQioemUvCMMiXBcZLu6Y4LkcXJY"

print("=" * 60)
print("CRIANDO WEB SERVICE AUTOMATICAMENTE")
print("=" * 60)

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Primeiro, vamos listar os serviços existentes para pegar as env vars
print("\nBuscando servico existente para copiar variaveis...")

try:
    response = requests.get(
        'https://api.render.com/v1/services',
        headers=headers
    )
    
    if response.status_code == 200:
        services = response.json()
        print(f"✅ Encontrados {len(services)} serviços")
        
        # Procurar pelo serviço caosbot
        old_service = None
        for service in services:
            if 'caosbot' in service.get('service', {}).get('name', '').lower():
                old_service = service['service']
                print(f"✅ Encontrado: {old_service['name']}")
                break
        
        if old_service:
            service_id = old_service['id']
            print(f"📍 ID do serviço: {service_id}")
            
            # Buscar env vars do serviço antigo
            print("\n📍 Copiando variáveis de ambiente...")
            env_response = requests.get(
                f'https://api.render.com/v1/services/{service_id}/env-vars',
                headers=headers
            )
            
            if env_response.status_code == 200:
                env_vars_data = env_response.json()
                env_vars = []
                
                for env in env_vars_data:
                    var = env.get('envVar', {})
                    env_vars.append({
                        'key': var.get('key'),
                        'value': var.get('value', '')
                    })
                
                print(f"✅ Copiadas {len(env_vars)} variáveis!")
                
                # Criar novo serviço WEB
                print("\n📍 Criando novo WEB SERVICE...")
                
                owner_id = old_service.get('ownerId')
                
                new_service = {
                    "type": "web_service",
                    "name": "caosbot-web-service",
                    "ownerId": owner_id,
                    "repo": "https://github.com/megacavaleiro6662-hub/caosbot-discord",
                    "branch": "main",
                    "rootDir": "",
                    "envVars": env_vars,
                    "serviceDetails": {
                        "runtime": "python",
                        "buildCommand": "",
                        "startCommand": "python caosbot_railway.py",
                        "plan": "free",
                        "region": "oregon",
                        "env": "python"
                    }
                }
                
                create_response = requests.post(
                    'https://api.render.com/v1/services',
                    headers=headers,
                    json=new_service
                )
                
                if create_response.status_code in [200, 201]:
                    result = create_response.json()
                    new_url = result.get('service', {}).get('serviceDetails', {}).get('url', '')
                    
                    print("\n" + "=" * 60)
                    print("✅ SUCESSO! WEB SERVICE CRIADO!")
                    print("=" * 60)
                    print(f"\n🌐 URL do Dashboard: {new_url}")
                    print(f"📍 Nome: caosbot-web-service")
                    print("\n⏰ Aguarde 5-10 minutos para o deploy!")
                    print("\n📝 PRÓXIMO PASSO:")
                    print("   Atualize o DISCORD_REDIRECT_URI para:")
                    print(f"   {new_url}/callback")
                    print("\n💡 Depois pode deletar o serviço antigo!")
                else:
                    print(f"\n❌ Erro ao criar: {create_response.status_code}")
                    print(f"Resposta: {create_response.text}")
            else:
                print(f"❌ Erro ao buscar env vars: {env_response.status_code}")
        else:
            print("❌ Serviço caosbot não encontrado!")
            print("\n📋 Serviços disponíveis:")
            for service in services:
                print(f"   - {service.get('service', {}).get('name')}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
