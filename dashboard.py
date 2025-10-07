from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

CONFIG_FILE = "welcome_config.json"
TICKET_CONFIG_FILE = "ticket_config.json"

def load_config():
    """Carrega configurações do arquivo"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'welcome_enabled': False,
        'goodbye_enabled': False,
        'autorole_enabled': False,
        'tickets_enabled': False,
        'status_message_id': None
    }

def save_config(config):
    """Salva configurações no arquivo"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """Página principal do dashboard"""
    config = load_config()
    return render_template('dashboard.html', config=config)

@app.route('/api/config/status', methods=['GET'])
def get_status():
    """Retorna status atual das configurações"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config/toggle', methods=['POST'])
def toggle_config():
    """Alterna estado de uma configuração"""
    data = request.get_json()
    key = data.get('key')
    
    if not key:
        return jsonify({'success': False, 'message': 'Key não fornecida'}), 400
    
    config = load_config()
    
    if key not in config:
        return jsonify({'success': False, 'message': 'Key inválida'}), 400
    
    # Alternar estado
    config[key] = not config[key]
    save_config(config)
    
    return jsonify({
        'success': True,
        'key': key,
        'new_value': config[key],
        'message': f'{key} agora está {"ativado" if config[key] else "desativado"}'
    })

@app.route('/api/config/update', methods=['POST'])
def update_config():
    """Atualiza múltiplas configurações de uma vez"""
    data = request.get_json()
    config = load_config()
    
    # Atualizar apenas chaves válidas
    valid_keys = ['welcome_enabled', 'goodbye_enabled', 'autorole_enabled', 'tickets_enabled']
    updated = []
    
    for key in valid_keys:
        if key in data:
            config[key] = bool(data[key])
            updated.append(key)
    
    save_config(config)
    
    return jsonify({
        'success': True,
        'updated': updated,
        'config': config,
        'message': f'{len(updated)} configurações atualizadas'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Dashboard',
        'version': '2.0'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
