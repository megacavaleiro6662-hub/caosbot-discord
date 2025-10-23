# -*- coding: utf-8 -*-
# Corrigir sincronização do splash screen e adicionar "Dashboard Carregado" no final

with open('caosbot_railway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Código antigo do splash
old_splash_code = '''            // 🎬 SISTEMA DE MENSAGENS E IMAGENS ROTATIVAS
            const loadingMessages = [
                { text: '⚡ Inicializando sistemas...', img: '{ROBITO_IMAGES["acenando"]}', progress: 20 },
                { text: '🔧 Configurando módulos...', img: '{ROBITO_IMAGES["feliz"]}', progress: 40 },
                { text: '📊 Coletando informações...', img: '{ROBITO_IMAGES["nervoso"]}', progress: 60 },
                { text: '🎨 Preparando interface...', img: '{ROBITO_IMAGES["feliz"]}', progress: 80 },
                { text: '✅ Finalizando carregamento...', img: '{ROBITO_IMAGES["dab"]}', progress: 100 }
            ];
            
            let currentMessageIndex = 0;
            const splashText = document.querySelector('.splash-text');
            const splashLogo = document.querySelector('.splash-logo');
            const progressBar = document.querySelector('.splash-progress-bar');
            
            function updateLoadingMessage() {
                if (currentMessageIndex >= loadingMessages.length) {
                    // Todas as mensagens exibidas - iniciar transição
                    setTimeout(function() {
                        if (splash) {
                            splash.classList.add('fade-out');
                            console.log('🎆 Transição épica iniciando...');
                            
                            setTimeout(function() {
                                splash.style.display = 'none';
                                console.log('✅ Dashboard carregado com sucesso!');
                            }, 1500);
                        }
                    }, 1000);
                    
                    // Ativar Robito
                    setTimeout(function() {
                        if (helper) {
                            helper.classList.add('entry-complete');
                            console.log('🤖 Robito ativo!');
                        }
                    }, 2000);
                    return;
                }
                
                const message = loadingMessages[currentMessageIndex];
                
                // Fade out
                splashText.classList.add('fade-transition');
                splashLogo.classList.add('fade-transition');
                
                setTimeout(function() {
                    // Atualizar conteúdo
                    splashText.textContent = message.text;
                    splashLogo.src = message.img;
                    progressBar.style.width = message.progress + '%';
                    
                    // Fade in
                    splashText.classList.remove('fade-transition');
                    splashLogo.classList.remove('fade-transition');
                    
                    console.log('📝 ' + message.text + ' (' + message.progress + '%)');
                    
                    currentMessageIndex++;
                    
                    // Próxima mensagem em 1.6 segundos
                    setTimeout(updateLoadingMessage, 1600);
                }, 600);
            }
            
            // Iniciar rotação de mensagens após 500ms
            setTimeout(updateLoadingMessage, 500);'''

# Novo código otimizado
new_splash_code = '''            // 🎬 SISTEMA DE MENSAGENS E IMAGENS ROTATIVAS (OTIMIZADO)
            const loadingMessages = [
                { text: '⚡ Inicializando sistemas...', img: '{ROBITO_IMAGES["acenando"]}', progress: 20 },
                { text: '🔧 Configurando módulos...', img: '{ROBITO_IMAGES["feliz"]}', progress: 40 },
                { text: '📊 Coletando informações...', img: '{ROBITO_IMAGES["nervoso"]}', progress: 60 },
                { text: '🎨 Preparando interface...', img: '{ROBITO_IMAGES["feliz"]}', progress: 80 },
                { text: '✅ Finalizando carregamento...', img: '{ROBITO_IMAGES["dab"]}', progress: 100 }
            ];
            
            let currentMessageIndex = 0;
            const splashText = document.querySelector('.splash-text');
            const splashLogo = document.querySelector('.splash-logo');
            const progressBar = document.querySelector('.splash-progress-bar');
            
            function updateLoadingMessage() {
                if (currentMessageIndex >= loadingMessages.length) {
                    // TODAS MENSAGENS EXIBIDAS - MOSTRAR "DASHBOARD CARREGADO"
                    setTimeout(function() {
                        // Fade out texto/logo atuais
                        splashText.classList.add('fade-transition');
                        splashLogo.classList.add('fade-transition');
                        
                        setTimeout(function() {
                            // Mostrar mensagem final
                            splashText.textContent = '✨ DASHBOARD CARREGADO! ✨';
                            splashText.style.fontSize = '28px';
                            splashText.style.fontWeight = '800';
                            splashLogo.src = '{ROBITO_IMAGES["dab"]}';
                            
                            // Fade in
                            splashText.classList.remove('fade-transition');
                            splashLogo.classList.remove('fade-transition');
                            
                            console.log('✨ DASHBOARD CARREGADO!');
                            
                            // Após 2 segundos, iniciar fade-out do splash
                            setTimeout(function() {
                                if (splash) {
                                    splash.classList.add('fade-out');
                                    console.log('🎆 Transição para dashboard...');
                                    
                                    setTimeout(function() {
                                        splash.style.display = 'none';
                                        console.log('✅ Splash removido!');
                                    }, 1500);
                                }
                                
                                // Ativar Robito
                                if (helper) {
                                    helper.classList.add('entry-complete');
                                    console.log('🤖 Robito ativo!');
                                }
                            }, 2000);
                        }, 400);
                    }, 800);
                    return;
                }
                
                const message = loadingMessages[currentMessageIndex];
                
                // Fade out SINCRONIZADO
                requestAnimationFrame(() => {
                    splashText.classList.add('fade-transition');
                    splashLogo.classList.add('fade-transition');
                });
                
                setTimeout(function() {
                    // Atualizar conteúdo SINCRONIZADO
                    requestAnimationFrame(() => {
                        splashText.textContent = message.text;
                        splashLogo.src = message.img;
                        progressBar.style.width = message.progress + '%';
                        
                        // Fade in
                        setTimeout(() => {
                            splashText.classList.remove('fade-transition');
                            splashLogo.classList.remove('fade-transition');
                        }, 50);
                    });
                    
                    console.log('📝 ' + message.text + ' (' + message.progress + '%)');
                    
                    currentMessageIndex++;
                    
                    // Próxima mensagem em 1.2 segundos (MENOS LAG)
                    setTimeout(updateLoadingMessage, 1200);
                }, 400);
            }
            
            // Iniciar rotação de mensagens após 300ms
            setTimeout(updateLoadingMessage, 300);'''

if old_splash_code in content:
    content = content.replace(old_splash_code, new_splash_code)
    print("[OK] Splash screen otimizado e sincronizado!")
else:
    print("[ERRO] Codigo nao encontrado!")

with open('caosbot_railway.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCESSO] Splash corrigido!")
print("")
print("MUDANCAS:")
print("1. 'Dashboard Carregado' aparece DEPOIS dos 100%")
print("2. Timing reduzido: 1200ms (antes 1600ms) - MENOS LAG")
print("3. Sincronizacao com requestAnimationFrame")
print("4. Fade otimizado: 400ms (antes 600ms)")
print("5. Mensagem final fica 2 segundos antes do fade-out")
