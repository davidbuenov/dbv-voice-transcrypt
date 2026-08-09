// =============================================================================
// DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
// Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Manejo de Tema Claro / Oscuro
    const themeToggle = document.getElementById('theme-toggle');
    const root = document.documentElement;
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = root.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', newTheme);
    });

    // Referencias al DOM para Drag and Drop y subida
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.getElementById('upload-progress');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercent = document.getElementById('progress-percent');
    const statusMessage = document.getElementById('status-message');
    const statusConsole = document.getElementById('status-console');
    const fileNameDisplay = document.getElementById('file-name-display');
    
    // Resultados
    const resultSection = document.getElementById('result-section');
    const transcriptionText = document.getElementById('transcription-text');
    const copyBtn = document.getElementById('copy-btn');
    
    // IA
    const aiSection = document.getElementById('ai-section');
    const aiModel = document.getElementById('ai-model');
    const apiKeyInput = document.getElementById('api-key');
    const saveKeyBtn = document.getElementById('save-key-btn');
    const aiOptionCards = document.querySelectorAll('.ai-option-card');
    const aiResultContainer = document.getElementById('ai-result-container');
    const aiResultContent = document.getElementById('ai-result-content');
    const copyAiBtn = document.getElementById('copy-ai-btn');

    // Custom Prompt
    const customPromptContainer = document.getElementById('custom-prompt-container');
    const customPromptInput = document.getElementById('custom-prompt-input');
    const runCustomPromptBtn = document.getElementById('run-custom-prompt-btn');

    // Multi-archivo / Sesión


    const fileListContainer = document.getElementById('file-list-container');
    const fileList = document.getElementById('file-list');
    const processSessionBtn = document.getElementById('process-session-btn');
    const clearSessionBtn = document.getElementById('clear-session-btn');
    
    let fileQueue = []; // Almacena objetos { file, status, transcription }
    let isProcessing = false;


    // Función de log en consola
    function logToConsole(message, isError = false) {
        const time = new Date().toLocaleTimeString();
        const span = document.createElement('span');
        span.textContent = `[${time}] ${message}`;
        if (isError) span.classList.add('error');
        statusConsole.appendChild(span);
        statusConsole.scrollTop = statusConsole.scrollHeight;
    }

    // Eventos Click y Drag&Drop
    dropzone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', (e) => {
        if(e.target.files.length) handleFiles(e.target.files);
    });

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length === 0) return;
        
        // Añadir nuevos archivos a la cola
        for (let i = 0; i < files.length; i++) {
            fileQueue.push({
                file: files[i],
                status: 'pending',
                transcription: ''
            });
        }
        
        renderFileList();
    }

    function renderFileList() {
        fileList.innerHTML = '';
        
        if (fileQueue.length === 0) {
            fileListContainer.classList.add('hidden');
            processSessionBtn.disabled = true;
            return;
        }

        fileListContainer.classList.remove('hidden');
        processSessionBtn.disabled = isProcessing;
        clearSessionBtn.disabled = isProcessing;

        fileQueue.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = `file-item ${item.status}`;
            
            const iconName = item.status === 'done' ? 'check-circle' : (item.status === 'processing' ? 'loader' : 'file-audio');

            li.innerHTML = `
                ${Icons.svg(iconName, 18)}
                <span class="file-name">${item.file.name}</span>
                <div class="file-controls">
                    ${!isProcessing ? `
                        <button class="control-btn" onclick="moveFile(${index}, -1)" title="Subir">
                            ${Icons.svg('chevron-up', 14)}
                        </button>
                        <button class="control-btn" onclick="moveFile(${index}, 1)" title="Bajar">
                            ${Icons.svg('chevron-down', 14)}
                        </button>
                        <button class="control-btn" onclick="removeFile(${index})" title="Eliminar">
                            ${Icons.svg('x', 14)}
                        </button>
                    ` : ''}
                </div>
            `;
            fileList.appendChild(li);
        });
    }

    window.moveFile = (index, direction) => {
        const newIndex = index + direction;
        if (newIndex >= 0 && newIndex < fileQueue.length) {
            const temp = fileQueue[index];
            fileQueue[index] = fileQueue[newIndex];
            fileQueue[newIndex] = temp;
            renderFileList();
        }
    };

    window.removeFile = (index) => {
        fileQueue.splice(index, 1);
        renderFileList();
    };

    clearSessionBtn.addEventListener('click', () => {
        fileQueue = [];
        renderFileList();
        resultSection.classList.add('hidden');
        aiSection.classList.add('hidden');
    });

    processSessionBtn.addEventListener('click', async () => {
        if (isProcessing) return;
        isProcessing = true;
        renderFileList();
        
        resultSection.classList.add('hidden');
        aiSection.classList.add('hidden');
        transcriptionText.textContent = '';
        statusConsole.innerHTML = '';
        
        logToConsole(`Iniciando procesamiento de sesión (${fileQueue.length} archivos)...`);

        for (let i = 0; i < fileQueue.length; i++) {
            fileQueue[i].status = 'processing';
            renderFileList();
            
            try {
                const text = await uploadAndTranscribe(fileQueue[i].file);
                fileQueue[i].transcription = text;
                fileQueue[i].status = 'done';
            } catch (error) {
                fileQueue[i].status = 'error';
                logToConsole(`Error en archivo ${fileQueue[i].file.name}: ${error}`, true);
                break;
            }
            renderFileList();
        }

        isProcessing = false;
        renderFileList();
        
        // Consolidar resultados
        const fullTranscript = fileQueue
            .filter(f => f.status === 'done')
            .map(f => f.transcription)
            .join('\n\n---\n\n');
            
        if (fullTranscript) {
            showResult(fullTranscript);
            logToConsole('Sesión completada. Puedes analizar los resultados conjuntos ahora.');
        }
    });

    async function uploadAndTranscribe(file) {
        return new Promise((resolve, reject) => {
            const url = '/upload';
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);
            
            fileNameDisplay.textContent = file.name;
            progressContainer.classList.remove('hidden');
            progressBarFill.style.width = '0%';
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded * 100.0) / e.total);
                    progressBarFill.style.width = percent + '%';
                    progressPercent.textContent = percent + '%';
                }
            });
            
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        logToConsole(`Archivo ${file.name} subido. Transcribiendo...`);
                        startTranscriptionWS(file.name, resolve, reject);
                    } else {
                        reject('Error en subida');
                    }
                }
            });
            
            xhr.open('POST', url, true);
            xhr.send(formData);
        });
    }

    function startTranscriptionWS(filename, resolve, reject) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || '127.0.0.1:8000';
        const wsUrl = `${protocol}//${host}/ws/transcribe`;
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => ws.send(filename);
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.status === 'success') {
                    ws.close();
                    resolve(data.text);
                } else if (data.status === 'error') {
                    ws.close();
                    reject(data.message);
                }
            } catch (e) {
                logToConsole(`[${filename}] ${event.data}`);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            reject('Error de conexión');
        };
    }

    function showResult(text) {
        progressContainer.classList.add('hidden');
        dropzone.style.display = 'flex';
        resultSection.classList.remove('hidden');
        aiSection.classList.remove('hidden'); // Mostrar panel de IA
        transcriptionText.textContent = text;
        // Restaurar botón por si se copia de nuevo
        copyBtn.textContent = 'Copiar Texto';
    }

    // Copiar al portapapeles
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(transcriptionText.textContent).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '¡Copiado!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });

    // Lógica de Inteligencia Artificial: cada proveedor cloud guarda su propia
    // API Key en localStorage bajo su propio namespace (ej. "openai_api_key"),
    // para no enviar por error la clave de un proveedor a otro al cambiar de modelo.
    function currentProvider() {
        const selectedOption = aiModel.options[aiModel.selectedIndex];
        return selectedOption.dataset.provider || 'gemini';
    }

    function apiKeyStorageName(provider) {
        return `${provider}_api_key`;
    }

    saveKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        const storageName = apiKeyStorageName(currentProvider());
        if (key) {
            localStorage.setItem(storageName, key);
            saveKeyBtn.textContent = 'Guardada';
            saveKeyBtn.classList.remove('btn-secondary');
            saveKeyBtn.classList.add('btn-primary');
            setTimeout(() => {
                saveKeyBtn.textContent = 'Guardar Key';
                saveKeyBtn.classList.add('btn-secondary');
                saveKeyBtn.classList.remove('btn-primary');
            }, 2000);
        } else {
            localStorage.removeItem(storageName);
            saveKeyBtn.textContent = 'Borrada';
            setTimeout(() => saveKeyBtn.textContent = 'Guardar Key', 2000);
        }
    });

    aiModel.addEventListener('change', () => {
        const provider = currentProvider();
        if (provider === 'gemma-local') {
            apiKeyInput.classList.add('hidden');
            saveKeyBtn.classList.add('hidden');
        } else {
            apiKeyInput.classList.remove('hidden');
            saveKeyBtn.classList.remove('hidden');
            apiKeyInput.value = localStorage.getItem(apiKeyStorageName(provider)) || '';
        }
    });

    // Disparar el evento una vez para inicializar el estado correcto
    aiModel.dispatchEvent(new Event('change'));

    aiOptionCards.forEach(card => {
        card.addEventListener('click', async () => {
            handleAiAnalysis(card);
        });
    });

    runCustomPromptBtn.addEventListener('click', () => {
        const customCard = Array.from(aiOptionCards).find(c => c.dataset.type === 'custom');
        if (customCard) handleAiAnalysis(customCard);
    });

    async function handleAiAnalysis(card) {
            const selectedOption = aiModel.options[aiModel.selectedIndex];
            const provider = currentProvider();
            const key = apiKeyInput.value.trim();

            if (provider !== 'gemma-local' && !key) {
                alert(`Por favor, introduce tu API Key de ${selectedOption.textContent} primero.`);
                apiKeyInput.focus();
                return;
            }

            const text = transcriptionText.textContent;
            if (!text || text.trim() === '') {
                alert('No hay transcripción disponible para analizar.');
                return;
            }

            // UI
            aiOptionCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            
            // Mostrar/ocultar textarea si es prompt personalizado
            const isCustom = card.dataset.type === 'custom';
            if (isCustom) {
                customPromptContainer.classList.remove('hidden');
                customPromptInput.focus();
            } else {
                customPromptContainer.classList.add('hidden');
            }

            // No ejecutar análisis inmediatamente si es custom y está vacío (y no se pulsó el botón Run)
            // Nota: El botón Run fuerza la ejecución.
            if (isCustom && !customPromptInput.value.trim()) {
                aiResultContainer.classList.add('hidden');
                return;
            }
            
            aiResultContainer.classList.remove('hidden');
            const modelName = selectedOption.textContent;
            aiResultContent.innerHTML = `<div style="text-align:center; padding:2rem;"><div class="loader"></div><p>Analizando con ${modelName}...</p></div>`;

            const cleanPrompt = customPromptInput.value.trim();
            logToConsole(`Enviando petición IA: [${card.dataset.type}] ${isCustom ? `"${cleanPrompt.substring(0, 30)}..."` : modelName}`);

            const payload = {
                text: text,
                provider: provider,
                model: aiModel.value,
                api_key: key || "local",
                transformation: card.dataset.type,
                custom_prompt: cleanPrompt
            };



            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Usar Marked.js si está disponible, si no texto plano
                    if (window.marked) {
                        aiResultContent.innerHTML = window.marked.parse(data.result);
                    } else {
                        aiResultContent.textContent = data.result;
                    }
                } else {
                    aiResultContent.innerHTML = `<p class="text-error">Error: ${data.detail || 'Fallo en la comunicación con la IA'}</p>`;
                }
            } catch (error) {
                aiResultContent.innerHTML = `<p class="text-error">Error de red: ${error.message}</p>`;
            }
    }


    copyAiBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(aiResultContent.innerText).then(() => {
            const originalText = copyAiBtn.textContent;
            copyAiBtn.textContent = '¡Copiado!';
            setTimeout(() => {
                copyAiBtn.textContent = originalText;
            }, 2000);
        });
    });
});
