#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT PARA CRIAR JSONBin E PEGAR O ID
Execute: python criar_bin_manual.py
"""

import requests
import json

JSONBIN_API_KEY = "$2a$10$OLp47wzSpJZqq7gAVgUgkO4qJQa6pAk6oL0pZ0OrV/Z.7HwQ/TRrq"
JSONBIN_API_URL = "https://api.jsonbin.io/v3/b"

print("=" * 60)
print("CRIANDO BIN NO JSONBIN.IO")
print("=" * 60)

# Configurações padrão
config_data = {
    'welcome_enabled': True,
    'goodbye_enabled': True,
    'autorole_enabled': False,
    'tickets_enabled': False
}

try:
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': JSONBIN_API_KEY
    }
    
    print("\n[1/2] Enviando requisição para criar bin...")
    response = requests.post(JSONBIN_API_URL, json=config_data, headers=headers)
    
    print(f"[2/2] Status da resposta: {response.status_code}")
    
    if response.status_code in [200, 201]:
        bin_id = response.json()['metadata']['id']
        
        print("\n" + "=" * 60)
        print("✅ BIN CRIADO COM SUCESSO!")
        print("=" * 60)
        print(f"\nJSONBIN_BIN_ID={bin_id}")
        print("\n" + "=" * 60)
        print("INSTRUÇÕES:")
        print("=" * 60)
        print("1. Copie o ID acima")
        print("2. Vá no Render Dashboard → Environment")
        print("3. Add Environment Variable")
        print("4. Key: JSONBIN_BIN_ID")
        print(f"5. Value: {bin_id}")
        print("6. Save Changes")
        print("7. Aguarde redeploy (~3 min)")
        print("8. PRONTO! Configs vão persistir! ✅")
        print("=" * 60)
    else:
        print(f"\n❌ ERRO AO CRIAR BIN")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

input("\nPressione ENTER para fechar...")
