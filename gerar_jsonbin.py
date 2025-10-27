import requests
import json

# Configurações
JSONBIN_API_KEY = "$2a$10$OLp47wzSpJZqq7gAVgUgkO4qJQa6pAk6oL0pZ0OrV/Z.7HwQ/TRrq"
JSONBIN_API_URL = "https://api.jsonbin.io/v3/b"

# Dados padrão
config_data = {
    "welcome_enabled": True,
    "goodbye_enabled": True,
    "autorole_enabled": True,
    "tickets_enabled": True
}

# Criar bin
headers = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_API_KEY
}

print("🔄 Criando JSONBin...")
response = requests.post(JSONBIN_API_URL, json=config_data, headers=headers)

if response.status_code in [200, 201]:
    bin_id = response.json()["metadata"]["id"]
    print("✅ BIN CRIADO COM SUCESSO!")
    print(f"JSONBIN_BIN_ID={bin_id}")
    print("")
    print("🔧 ADICIONE NO RENDER:")
    print(f"Key: JSONBIN_BIN_ID")
    print(f"Value: {bin_id}")
else:
    print(f"❌ ERRO: {response.status_code}")
    print(response.text)
