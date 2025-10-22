# -*- coding: utf-8 -*-
# Corrigir chaves inexistentes do ROBITO_IMAGES

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir chaves inexistentes por chaves que existem
replacements = [
    ('ROBITO_IMAGES["explicando"]', 'ROBITO_IMAGES["feliz"]'),
    ('ROBITO_IMAGES["pensando"]', 'ROBITO_IMAGES["nervoso"]'),
    ('ROBITO_IMAGES["comemorando"]', 'ROBITO_IMAGES["dab"]'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"[OK] {old} -> {new}")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCESSO] Chaves ROBITO_IMAGES corrigidas!")
