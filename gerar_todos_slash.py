# Script para listar TODOS os comandos do bot
import re

# Ler o arquivo
with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar todos os comandos
pattern = r"@bot\.command\(name='(\w+)'\)"
comandos = re.findall(pattern, content)

print(f"TOTAL DE COMANDOS ENCONTRADOS: {len(comandos)}\n")
print("LISTA DE COMANDOS:")
for i, cmd in enumerate(comandos, 1):
    print(f"{i}. .{cmd}")

print(f"\nTotal: {len(comandos)} comandos para converter!")
