/**
 * 🎮 DASHBOARD XP - JAVASCRIPT
 * Funções de interatividade, preview e API calls
 */

const GUILD_ID = window.location.pathname.split('/')[2];
const API_BASE = `/api/xp/${GUILD_ID}`;

// ==================== TABS ====================

document.addEventListener('DOMContentLoaded', function() {
    // Tab navigation
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            // Remove active from all
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            // Add active to clicked
            tab.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });
    
    // Announce mode radio buttons - show/hide custom channel
    const announceModeRadios = document.querySelectorAll('input[name="announce_mode"]');
    announceModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const customChannelGroup = document.getElementById('custom-channel-group');
            if (radio.value === 'custom' && radio.checked) {
                customChannelGroup.style.display = 'block';
            } else {
                customChannelGroup.style.display = 'none';
            }
        });
    });
    
    // Message preview - live update
    const messageTemplate = document.getElementById('message_template');
    if (messageTemplate) {
        messageTemplate.addEventListener('input', updateMessagePreview);
        updateMessagePreview(); // Initial render
    }
});

// ==================== API CALLS ====================

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ ' + result.message, 'success');
        } else {
            showToast('❌ ' + (result.message || 'Erro desconhecido'), 'error');
        }
        
        return result;
    } catch (error) {
        showToast('❌ Erro de conexão: ' + error.message, 'error');
        throw error;
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#00ff66' : type === 'error' ? '#ff0044' : '#0066ff'};
        color: ${type === 'success' ? '#000' : '#fff'};
        border: 2px solid ${type === 'success' ? '#00cc55' : type === 'error' ? '#cc0033' : '#00ccff'};
        font-weight: 700;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== TAB 1: GERAL ====================

async function saveGeneralConfig() {
    const data = {
        is_enabled: document.getElementById('is_enabled').checked,
        cooldown: parseInt(document.getElementById('cooldown').value),
        min_xp: parseInt(document.getElementById('min_xp').value),
        max_xp: parseInt(document.getElementById('max_xp').value),
        log_channel: document.getElementById('log_channel').value || null
    };
    
    await apiCall(`${API_BASE}/config/general`, 'POST', data);
}

async function resetAllXP() {
    if (!confirm('⚠️ ATENÇÃO! Esta ação é IRREVERSÍVEL!\n\nDeseja realmente ZERAR o XP de TODOS os usuários?')) {
        return;
    }
    
    const confirmText = prompt('Digite "CONFIRMAR RESET" para continuar:');
    if (confirmText !== 'CONFIRMAR RESET') {
        showToast('❌ Operação cancelada', 'error');
        return;
    }
    
    await apiCall(`${API_BASE}/reset`, 'POST');
    
    setTimeout(() => {
        window.location.reload();
    }, 2000);
}

// ==================== TAB 2: NÍVEIS ====================

async function saveLevels() {
    const levelItems = document.querySelectorAll('.level-item');
    const updates = [];
    
    levelItems.forEach(item => {
        const levelId = item.querySelector('input[data-field="role_name"]').getAttribute('data-level-id');
        const roleName = item.querySelector('input[data-field="role_name"]').value;
        const roleId = item.querySelector('input[data-field="role_id"]').value;
        const requiredXp = parseInt(item.querySelector('input[data-field="required_xp"]').value);
        const multiplier = parseFloat(item.querySelector('input[data-field="multiplier"]').value);
        
        updates.push({
            id: levelId,
            role_name: roleName,
            role_id: roleId,
            required_xp: requiredXp,
            multiplier: multiplier
        });
    });
    
    // Update each level
    for (const level of updates) {
        await apiCall(`${API_BASE}/levels/${level.id}`, 'PUT', level);
    }
    
    showToast('✅ Todos os níveis foram atualizados!', 'success');
}

async function addLevel() {
    const levelNumber = document.querySelectorAll('.level-item').length + 1;
    
    const data = {
        level: levelNumber,
        role_id: '0',
        role_name: `Nível ${levelNumber}`,
        required_xp: levelNumber * 1000,
        multiplier: 1.0
    };
    
    await apiCall(`${API_BASE}/levels`, 'POST', data);
    
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

async function deleteLevel(levelId) {
    if (!confirm('Deseja realmente deletar este nível?')) {
        return;
    }
    
    await apiCall(`${API_BASE}/levels/${levelId}`, 'DELETE');
    
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

// ==================== TAB 3: RECOMPENSAS ====================

async function saveRewards() {
    const rewardMode = document.querySelector('input[name="reward_mode"]:checked').value;
    const bonusOnLevelup = parseInt(document.getElementById('bonus_on_levelup').value);
    
    const data = {
        reward_mode: rewardMode,
        bonus_on_levelup: bonusOnLevelup
    };
    
    await apiCall(`${API_BASE}/config/rewards`, 'POST', data);
}

// ==================== TAB 4: BLOQUEIOS ====================

async function saveBlocks() {
    const blockedRoles = document.getElementById('blocked_roles').value
        .split(',')
        .map(id => id.trim())
        .filter(id => id);
    
    const blockedChannels = document.getElementById('blocked_channels').value
        .split(',')
        .map(id => id.trim())
        .filter(id => id);
    
    const data = {
        blocked_roles: blockedRoles,
        blocked_channels: blockedChannels
    };
    
    await apiCall(`${API_BASE}/config/blocks`, 'POST', data);
}

// ==================== TAB 5: MENSAGENS ====================

function updateMessagePreview() {
    const template = document.getElementById('message_template').value;
    const previewDiv = document.getElementById('message-preview');
    
    if (!previewDiv) return;
    
    // Replace placeholders with example values
    let preview = template
        .replace(/{user}/g, 'João')
        .replace(/{user_mention}/g, '@João')
        .replace(/{level}/g, '5')
        .replace(/{level_name}/g, 'épico')
        .replace(/{xp}/g, '2,500')
        .replace(/{next_level_xp}/g, '4,000')
        .replace(/{guild_name}/g, 'Meu Servidor');
    
    // Convert markdown-like syntax to HTML
    preview = preview
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    previewDiv.innerHTML = preview;
}

function insertPlaceholder(placeholder) {
    const textarea = document.getElementById('message_template');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    
    textarea.value = text.substring(0, start) + placeholder + text.substring(end);
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = start + placeholder.length;
    
    updateMessagePreview();
}

async function saveMessages() {
    const announceMode = document.querySelector('input[name="announce_mode"]:checked').value;
    const announceType = document.querySelector('input[name="announce_type"]:checked').value;
    const announceChannel = document.getElementById('announce_channel').value || null;
    const messageTemplate = document.getElementById('message_template').value;
    
    const data = {
        announce_mode: announceMode,
        announce_type: announceType,
        announce_channel: announceChannel,
        message_template: messageTemplate
    };
    
    await apiCall(`${API_BASE}/config/messages`, 'POST', data);
}

// ==================== TAB 6: RANK CARD ====================

async function saveRankCard() {
    const data = {
        image_bg_color: document.getElementById('image_bg_color').value,
        image_bg_url: document.getElementById('image_bg_url').value || null,
        image_bar_color: document.getElementById('image_bar_color').value,
        image_text_color: document.getElementById('image_text_color').value
    };
    
    await apiCall(`${API_BASE}/config/rankcard`, 'POST', data);
}

function previewRankCard() {
    showToast('🎨 Use o comando .xp no Discord para ver o preview!', 'info');
}

// ==================== TAB 7: ESTATÍSTICAS ====================

async function loadStats() {
    try {
        const stats = await fetch(`${API_BASE}/stats`).then(r => r.json());
        
        document.getElementById('total-xp').textContent = stats.total_xp.toLocaleString('pt-BR');
        document.getElementById('avg-xp').textContent = stats.avg_xp.toLocaleString('pt-BR');
        document.getElementById('total-messages').textContent = stats.total_messages.toLocaleString('pt-BR');
        
        // Render recent logs (if element exists)
        const logsContainer = document.getElementById('recent-logs');
        if (logsContainer && stats.recent_logs) {
            logsContainer.innerHTML = stats.recent_logs.map(log => `
                <div style="padding: 10px; border-bottom: 1px solid #0066ff;">
                    <strong>User ${log.user_id}</strong> ganhou <strong>${log.xp_gained} XP</strong>
                    <br>
                    <small>${new Date(log.timestamp).toLocaleString('pt-BR')}</small>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function exportCSV() {
    window.location.href = `${API_BASE}/export/csv`;
    showToast('📥 Baixando CSV...', 'success');
}

// ==================== TAB 8: BOOSTS ====================

async function createBoost() {
    const multiplier = parseFloat(prompt('Multiplicador de XP (ex: 2.0 para 2x):', '2.0'));
    const duration = parseInt(prompt('Duração em minutos:', '60'));
    
    if (!multiplier || !duration) {
        showToast('❌ Valores inválidos', 'error');
        return;
    }
    
    const data = {
        multiplier: multiplier,
        duration: duration
    };
    
    await apiCall(`${API_BASE}/boost`, 'POST', data);
    
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

// ==================== LOAD STATS ON TAB CHANGE ====================

document.addEventListener('DOMContentLoaded', () => {
    const statsTab = document.querySelector('.tab[data-tab="stats"]');
    if (statsTab) {
        statsTab.addEventListener('click', () => {
            setTimeout(loadStats, 100);
        });
    }
});

console.log('✅ Dashboard XP JavaScript carregado!');
