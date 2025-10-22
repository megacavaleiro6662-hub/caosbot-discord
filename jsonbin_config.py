# -*- coding: utf-8 -*-
"""
JSONBin Integration - Sistema de Persistência de Configurações
Salva configurações no JSONBin para persistir entre deploys
"""

import os
import requests

# Configuração JSONBin
JSONBIN_API_KEY = "$2a$10$OLp47wzSpJZqq7gAVgUgkO4qJQa6pAk6oL0pZ0OrV/Z.7HwQ/TRrq"
JSONBIN_BIN_ID = os.getenv('JSONBIN_BIN_ID', None)
JSONBIN_API_URL = "https://api.jsonbin.io/v3/b"

def save_config_to_jsonbin(config_data):
    """Salva configurações no JSONBin (PERSISTENTE)"""
    global JSONBIN_BIN_ID
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Master-Key': JSONBIN_API_KEY
        }
        
        if JSONBIN_BIN_ID:
            # Atualizar bin existente
            response = requests.put(
                f"{JSONBIN_API_URL}/{JSONBIN_BIN_ID}",
                json=config_data,
                headers=headers
            )
            print(f"[JSONBIN] Atualizando bin: {JSONBIN_BIN_ID}")
        else:
            # Criar novo bin
            response = requests.post(
                JSONBIN_API_URL,
                json=config_data,
                headers=headers
            )
            if response.status_code == 200:
                JSONBIN_BIN_ID = response.json()['metadata']['id']
                print(f"[JSONBIN] Bin criado! ID: {JSONBIN_BIN_ID}")
                print(f"[IMPORTANTE] Adicione no Render: JSONBIN_BIN_ID={JSONBIN_BIN_ID}")
        
        if response.status_code in [200, 201]:
            print(f"[JSONBIN] Configuracoes salvas com sucesso!")
            return True
        else:
            print(f"[JSONBIN] Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[JSONBIN] Erro ao salvar: {e}")
        return False

def load_config_from_jsonbin():
    """Carrega configurações do JSONBin"""
    if not JSONBIN_BIN_ID:
        print("[JSONBIN] BIN_ID não configurado. Usando padrão.")
        return None
    
    try:
        headers = {'X-Master-Key': JSONBIN_API_KEY}
        response = requests.get(
            f"{JSONBIN_API_URL}/{JSONBIN_BIN_ID}/latest",
            headers=headers
        )
        
        if response.status_code == 200:
            config = response.json()['record']
            print(f"[JSONBIN] Configuracoes carregadas com sucesso!")
            return config
        else:
            print(f"[JSONBIN] Erro ao carregar: {response.status_code}")
            return None
    except Exception as e:
        print(f"[JSONBIN] Erro ao carregar: {e}")
        return None
