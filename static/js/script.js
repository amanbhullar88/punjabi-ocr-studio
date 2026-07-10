document.addEventListener('DOMContentLoaded', function() {
    
    // ---------- Gemini API Key & Engine Manager ----------
    const settingsBtnTop = document.getElementById('settingsBtnTop');
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
    const clearApiKeyBtn = document.getElementById('clearApiKeyBtn');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const toggleApiKeyVisibility = document.getElementById('toggleApiKeyVisibility');
    const statusMessage = document.getElementById('statusMessage');

    // Load API Key
    let geminiApiKey = localStorage.getItem('gemini_api_key') || '';
    apiKeyInput.value = geminiApiKey;
    let serverHasApiKey = false;

    // Check if server has API key configured
    fetch('/has_api_key')
        .then(res => res.json())
        .then(data => {
            serverHasApiKey = !!data.has_key;
            updateSettingsUI();
        })
        .catch(err => console.error('Error checking server API key:', err));

    function updateSettingsUI() {
        const keyStatusBanner = document.getElementById('keyStatusBanner');
        if (keyStatusBanner) {
            keyStatusBanner.style.display = 'block';
            if (geminiApiKey) {
                keyStatusBanner.innerHTML = '🟢 Custom browser API Key is active (Overrides server key).';
                keyStatusBanner.style.color = '#34d399';
            } else if (serverHasApiKey) {
                keyStatusBanner.innerHTML = '🔵 Pre-configured Server API Key is active (No setup required).';
                keyStatusBanner.style.color = '#38bdf8';
            } else {
                keyStatusBanner.innerHTML = '🟡 No API Key configured. Paste a key below to enable Gemini AI OCR.';
                keyStatusBanner.style.color = '#fbbf24';
            }
        }
    }

    // Modal Events
    function openModal() {
        settingsModal.style.display = 'flex';
        apiKeyInput.value = localStorage.getItem('gemini_api_key') || '';
        updateSettingsUI();
    }
    function closeModal() {
        settingsModal.style.display = 'none';
    }

    if (settingsBtnTop) settingsBtnTop.addEventListener('click', openModal);
    closeSettingsBtn.addEventListener('click', closeModal);
    
    settingsModal.addEventListener('click', function(e) {
        if (e.target === settingsModal) closeModal();
    });

    // Save/Clear Key
    saveApiKeyBtn.addEventListener('click', function() {
        const key = apiKeyInput.value.trim();
        if (key) {
            localStorage.setItem('gemini_api_key', key);
            geminiApiKey = key;
            showStatus('✅ Gemini API Key saved!', 'success');
        } else {
            localStorage.removeItem('gemini_api_key');
            geminiApiKey = '';
            showStatus('ℹ️ Key cleared', 'info');
        }
        updateSettingsUI();
        closeModal();
    });

    clearApiKeyBtn.addEventListener('click', function() {
        localStorage.removeItem('gemini_api_key');
        geminiApiKey = '';
        apiKeyInput.value = '';
        showStatus('🗑️ Gemini API Key removed.', 'info');
        updateSettingsUI();
        closeModal();
    });

    // Show/Hide Password Toggle
    toggleApiKeyVisibility.addEventListener('click', function() {
        const type = apiKeyInput.type === 'password' ? 'text' : 'password';
        apiKeyInput.type = type;
        const icon = this.querySelector('i');
        icon.className = type === 'password' ? 'fa-regular fa-eye' : 'fa-regular fa-eye-slash';
    });

    // ---------- Textareas & Dynamic Preview Font Styler ----------
    const sourceText = document.getElementById('sourceText');
    const convertedText = document.getElementById('convertedText');
    const targetFontSelect = document.getElementById('targetFont');
    const autoConvertToggle = document.getElementById('autoConvertToggle');
    
    // Maps dropdown converter code to font-family declared in style.css
    const fontMapping = {
        'Unicode': "'Raavi'",
        'Asees': "'Asees'",
        'AnmolLipi': "'Anmol Lipi', 'AnmolLipi'",
        'Joy': "'Joy'",
        'GurbaniLipi': "'Gurbani Lipi', 'GurbaniLipi'",
        'AmritLipi': "'Amrit Lipi', 'AmritLipi', 'Anmol Lipi'",
        'Satluj': "'Satluj'",
        'AmarLipi': "'Amar Lipi', 'AmarLipi', 'Anmol Lipi'",
        'GurumukhiLys': "'Gurumukhi Lys 020', 'GurumukhiLys'"
    };

    function applyDynamicFont() {
        const selectedValue = targetFontSelect.value;
        const fontName = fontMapping[selectedValue] || 'inherit';
        
        // Style main div
        convertedText.style.fontFamily = fontName === 'inherit' ? 'inherit' : `${fontName}, Arial, sans-serif`;
        
        // Style children spans
        const legacySpans = convertedText.querySelectorAll('.font-legacy');
        legacySpans.forEach(span => {
            span.style.fontFamily = fontName === 'inherit' ? 'inherit' : `${fontName}, Arial, sans-serif`;
        });
    }

    targetFontSelect.addEventListener('change', applyDynamicFont);
    applyDynamicFont(); // Run on startup

    // ---------- Auto Convert Real-Time Conversion ----------
    // Load Auto Convert state
    const autoConvertSaved = localStorage.getItem('auto_convert');
    if (autoConvertSaved !== null) {
        autoConvertToggle.checked = autoConvertSaved === 'true';
    }

    autoConvertToggle.addEventListener('change', function() {
        localStorage.setItem('auto_convert', this.checked);
        if (this.checked) {
            triggerConversion();
        }
    });

    // Listen to source input
    sourceText.addEventListener('input', function() {
        if (autoConvertToggle.checked) {
            triggerConversion();
        }
    });

    // Listen to target font selection change
    targetFontSelect.addEventListener('change', function() {
        if (autoConvertToggle.checked) {
            triggerConversion();
        }
    });

    // Listen to source font selection change
    document.getElementById('sourceFont').addEventListener('change', function() {
        if (autoConvertToggle.checked) {
            triggerConversion();
        }
    });

    // Run conversion helper
    function triggerConversion() {
        const text = sourceText.value;
        if (!text.trim()) {
            convertedText.innerHTML = '';
            return;
        }
        const fromFont = document.getElementById('sourceFont').value;
        const toFont = targetFontSelect.value;

        fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, from_font: fromFont, to_font: toFont })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                convertedText.innerHTML = data.converted_html || data.converted;
                applyDynamicFont();
            }
        })
        .catch(err => console.error('Auto convert error:', err));
    }

    // ---------- Voice Recognition (Speech to Text) ----------
    let recognition = null;
    let isPaused = false;
    let isListening = false;

    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const voiceLang = document.getElementById('voiceLang');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        updateStatus('⚠️ Speech recognition not supported in this browser.', 'warning');
        startBtn.disabled = true;
    }

    startBtn.addEventListener('click', function() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Speech recognition not supported in this browser. Please use Safari on iOS.');
            return;
        }
        
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = voiceLang.value;
            
            // Detect iOS devices (iPhone, iPad, iPod)
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                          (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
            
            if (isIOS) {
                recognition.continuous = false; // iOS Safari fails with service-not-allowed if continuous is true!
                recognition.interimResults = true;
            } else {
                recognition.continuous = true;
                recognition.interimResults = true;
            }

            recognition.onstart = function() {
                isListening = true;
                isPaused = false;
                startBtn.disabled = true;
                stopBtn.disabled = false;
                pauseBtn.disabled = false;
                pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
                updateStatus(`🎤 Listening... (${voiceLang.options[voiceLang.selectedIndex].text})`, 'info');
            };

            recognition.onresult = function(event) {
                if (isPaused) return;
                let final = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        final += event.results[i][0].transcript + ' ';
                    }
                }
                if (final) {
                    sourceText.value += final;
                    // Trigger auto-conversion if active
                    if (autoConvertToggle.checked) {
                        triggerConversion();
                    }
                    sourceText.scrollTop = sourceText.scrollHeight;
                }
            };

            recognition.onerror = function(event) {
                console.error('Speech error:', event.error);
                let userMsg = event.error;
                if (event.error === 'not-allowed') {
                    userMsg = 'Microphone access blocked. Please allow mic in settings.';
                    alert('Microphone Access Blocked:\nPlease go to your iPhone Settings > Safari > Microphone, and change it to "Allow".');
                } else if (event.error === 'service-not-allowed') {
                    userMsg = 'iOS Speech Recognition Service Not Allowed.';
                    alert('iOS Speech Recognition Error:\n\n1. Ensure you are using the native SAFARI browser on iPhone. (Chrome, Firefox, or inside apps like WhatsApp/Facebook on iOS do NOT support Speech Recognition and will always fail with this error).\n2. If already using Safari, try closing other tabs or apps using the microphone.\n3. Make sure Siri is not actively listening.\n4. Try restarting Safari.');
                } else {
                    updateStatus(`❌ Error: ${userMsg}`, 'danger');
                }
                
                // Safe manual stop without wiping error message
                if (recognition) {
                    try { recognition.stop(); } catch(e) {}
                    recognition = null;
                }
                isListening = false;
                isPaused = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                pauseBtn.disabled = true;
                pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
            };

            recognition.onend = function() {
                if (isListening && !isPaused) {
                    try {
                        recognition.start();
                    } catch(e) {
                        console.error('Failed to restart speech recognition:', e);
                        stopListening();
                    }
                } else {
                    stopListening();
                }
            };

            recognition.start();
        } catch (err) {
            console.error('Speech Recognition Initialization Error:', err);
            alert('Speech Recognition could not be started: ' + err.message);
            updateStatus(`❌ Error: ${err.message}`, 'danger');
            isListening = false;
            isPaused = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            pauseBtn.disabled = true;
        }
    });

    function stopListening() {
        if (recognition) {
            recognition.stop();
            recognition = null;
        }
        isListening = false;
        isPaused = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        pauseBtn.disabled = true;
        pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
        updateStatus('⏹ Stopped voice transcription', 'success');
    }

    stopBtn.addEventListener('click', stopListening);

    pauseBtn.addEventListener('click', function() {
        if (!recognition) return;
        isPaused = !isPaused;
        if (isPaused) {
            pauseBtn.innerHTML = '<i class="fa-solid fa-play"></i> Resume';
            updateStatus('⏸ Voice typing paused', 'warning');
        } else {
            pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
            updateStatus('🎤 Voice typing resumed...', 'info');
        }
    });

    // ---------- Camera Scanning Module ----------
    const cameraBtn = document.getElementById('cameraBtn');
    const cameraContainer = document.getElementById('cameraContainer');
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('captureBtn');
    const closeCamBtn = document.getElementById('closeCamBtn');
    let videoStream = null;

    cameraBtn.addEventListener('click', async function() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('Camera access is not supported in this browser or environment (e.g. Chrome on iOS or insecure context). Please use Safari on iOS.');
            updateStatus('❌ Camera error: getUserMedia not supported', 'danger');
            return;
        }
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            video.srcObject = videoStream;
            cameraContainer.style.display = 'block';
            updateStatus('📷 Camera initialized - hold document steady', 'info');
        } catch (err) {
            updateStatus('❌ Camera error: ' + err.message, 'danger');
            alert('Could not access camera. Please grant camera permissions.');
        }
    });

    function stopCamera() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }
        cameraContainer.style.display = 'none';
        updateStatus('📷 Camera closed', 'info');
    }

    closeCamBtn.addEventListener('click', stopCamera);

    captureBtn.addEventListener('click', function() {
        if (!videoStream) {
            alert('Camera not started.');
            return;
        }
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(function(blob) {
            if (!blob) {
                updateStatus('❌ Page capture failed', 'danger');
                return;
            }
            const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
            uploadFile(file);
            stopCamera();
        }, 'image/jpeg');
    });

    // ---------- File Upload Module ----------
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');

    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;
        uploadFile(file);
        this.value = '';
    });

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        let statusMsg = (geminiApiKey || serverHasApiKey) 
            ? `📤 Loaded: ${file.name} (Running Gemini AI OCR...)`
            : `📤 Loaded: ${file.name} (Running offline OCR...)`;
        
        updateStatus(statusMsg, 'info');

        fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Gemini-API-Key': geminiApiKey // Send header if present
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                updateStatus('❌ Error: ' + data.error, 'danger');
                alert(data.error);
                return;
            }

            sourceText.value = data.text;
            if (autoConvertToggle.checked) {
                triggerConversion();
            } else {
                convertedText.innerText = data.text;
            }

            updateStatus(`📂 Loaded: ${file.name}`, 'success');

            // DOCX formatting download banner setup
            if (data.file_type === 'docx' && data.file_b64) {
                window._docxData = data.file_b64;
                const container = document.getElementById('docxConvertContainer');
                let btn = document.getElementById('convertDocxBtn');
                if (!btn) {
                    btn = document.createElement('button');
                    btn.id = 'convertDocxBtn';
                    btn.className = 'btn btn-docx-dl';
                    btn.innerHTML = '<i class="fa-solid fa-file-shield"></i> Convert DOCX Structure & Download File';
                    container.appendChild(btn);
                    btn.addEventListener('click', convertDocx);
                }
            } else {
                window._docxData = null;
                const btn = document.getElementById('convertDocxBtn');
                if (btn) btn.remove();
            }
        })
        .catch(err => {
            updateStatus('❌ Upload/Processing failed', 'danger');
            console.error(err);
        });
    }

    // ---------- Text Font Converter Button Call ----------
    const convertBtn = document.getElementById('convertBtn');

    convertBtn.addEventListener('click', function() {
        const text = sourceText.value;
        if (!text.trim()) {
            alert('Please enter some text in the source box.');
            return;
        }
        const fromFont = document.getElementById('sourceFont').value;
        const toFont = targetFontSelect.value;

        convertBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Converting...';
        convertBtn.disabled = true;
        updateStatus('🔄 Converting font...', 'info');

        fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, from_font: fromFont, to_font: toFont })
        })
        .then(res => res.json())
        .then(data => {
            convertBtn.innerHTML = '<i class="fa-solid fa-arrow-right-arrow-left"></i> Convert';
            convertBtn.disabled = false;
            if (data.error) {
                updateStatus('❌ Conversion error', 'danger');
                alert('Conversion error: ' + data.error);
            } else {
                convertedText.innerHTML = data.converted_html || data.converted;
                applyDynamicFont();
                updateStatus('✅ Font converted successfully!', 'success');
            }
        })
        .catch(err => {
            convertBtn.innerHTML = '<i class="fa-solid fa-arrow-right-arrow-left"></i> Convert';
            convertBtn.disabled = false;
            updateStatus('❌ Request failed', 'danger');
            alert('Request failed: ' + err);
        });
    });

    // ---------- Translation Engine Call ----------
    const translateBtn = document.getElementById('translateBtn');
    const translateSrc = document.getElementById('translateSrc');
    const destLang = document.getElementById('destLang');
    const translationResultContainer = document.getElementById('translationResultContainer');
    const translationResult = document.getElementById('translationResult');
    const closeTranslationBtn = document.getElementById('closeTranslationBtn');

    translateBtn.addEventListener('click', function() {
        const text = sourceText.value;
        if (!text.trim()) {
            alert('Please enter some text to translate.');
            return;
        }
        const src = translateSrc.value;
        const dest = destLang.value;
        updateStatus('🔄 Translating...', 'info');
        translateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Translating...';
        translateBtn.disabled = true;

        fetch('/translate', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-Gemini-API-Key': geminiApiKey
            },
            body: JSON.stringify({ text, src, dest })
        })
        .then(res => res.json())
        .then(data => {
            translateBtn.innerHTML = '<i class="fa-solid fa-file-invoice"></i> Translate';
            translateBtn.disabled = false;
            if (data.error) {
                updateStatus('❌ Translation failed', 'danger');
                alert('Translation error: ' + data.error);
            } else {
                // Replace newlines with br tags for rich container layout rendering
                const htmlTranslation = data.translation.replace(/\r?\n/g, '<br>');
                
                // Render directly in the Output container wrapped in the font-english class
                convertedText.innerHTML = `<span class="font-english">${htmlTranslation}</span>`;
                
                // Force output font-family to standard English sans-serif
                convertedText.style.fontFamily = "'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif";
                
                updateStatus('✅ Translation completed!', 'success');
            }
        })
        .catch(err => {
            translateBtn.innerHTML = '<i class="fa-solid fa-file-invoice"></i> Translate';
            translateBtn.disabled = false;
            updateStatus('❌ Translation request failed', 'danger');
            alert('Request failed: ' + err);
        });
    });

    if (closeTranslationBtn) {
        closeTranslationBtn.addEventListener('click', function() {
            if (translationResultContainer) translationResultContainer.style.display = 'none';
        });
    }

    // ---------- Copy & Export Actions ----------
    document.getElementById('copySrcBtn').addEventListener('click', function() {
        navigator.clipboard.writeText(sourceText.value).then(() => {
            showStatus('📋 Source text copied to clipboard!', 'success');
        });
    });
    
    document.getElementById('clearBtn').addEventListener('click', function() {
        sourceText.value = '';
        convertedText.innerHTML = '';
        showStatus('🗑️ Workspace cleared', 'info');
    });

    document.getElementById('copyConvBtn').addEventListener('click', function() {
        const selectedValue = targetFontSelect.value;
        const fontName = fontMapping[selectedValue] || 'inherit';
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = convertedText.innerHTML.replace(/\r?\n/g, '<br>');
        
        const legacySpans = tempDiv.querySelectorAll('.font-legacy');
        legacySpans.forEach(span => {
            span.style.fontFamily = fontName === 'inherit' ? 'inherit' : `${fontName}, Arial, sans-serif`;
        });
        
        const englishSpans = tempDiv.querySelectorAll('.font-english');
        englishSpans.forEach(span => {
            span.style.fontFamily = "'Arial', 'Calibri', sans-serif";
        });

        const formattedHtml = tempDiv.innerHTML;
        const plainText = convertedText.innerText;

        // Try Clipboard API with ClipboardItem first (modern standard)
        if (navigator.clipboard && window.ClipboardItem) {
            const htmlBlob = new Blob([formattedHtml], { type: 'text/html' });
            const textBlob = new Blob([plainText], { type: 'text/plain;charset=utf-8' });
            const item = new ClipboardItem({
                'text/html': htmlBlob,
                'text/plain': textBlob
            });

            navigator.clipboard.write([item]).then(() => {
                showStatus('📋 Formatted Rich Text copied! (Ready to paste in MS Word)', 'success');
            }).catch(err => {
                console.warn('ClipboardItem copy failed, trying fallback:', err);
                fallbackCopy(formattedHtml, plainText);
            });
        } else {
            fallbackCopy(formattedHtml, plainText);
        }
    });

    function fallbackCopy(htmlContent, plainText) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent;
        tempDiv.style.position = 'absolute';
        tempDiv.style.left = '-9999px';
        tempDiv.style.top = '-9999px';
        tempDiv.style.whiteSpace = 'pre-wrap';
        document.body.appendChild(tempDiv);
        
        const range = document.createRange();
        range.selectNodeContents(tempDiv);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showStatus('📋 Formatted Rich Text copied! (Ready to paste in MS Word)', 'success');
            } else {
                throw new Error('execCommand returned false');
            }
        } catch (err) {
            console.error('Fallback execCommand failed:', err);
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(plainText).then(() => {
                    showStatus('📋 Copied plain text', 'success');
                }).catch(e => {
                    alert('Copy failed. Please manually select and copy the text.');
                });
            } else {
                alert('Copy failed. Please manually select and copy the text.');
            }
        }
        
        selection.removeAllRanges();
        document.body.removeChild(tempDiv);
    }

    document.getElementById('exportBtn').addEventListener('click', function() {
        const text = convertedText.innerText;
        if (!text.trim()) {
            alert('Nothing to export.');
            return;
        }
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'converted_output.txt';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        updateStatus('📄 Output text file downloaded!', 'success');
    });

    document.getElementById('exportDocBtn').addEventListener('click', function() {
        const selectedValue = targetFontSelect.value;
        const fontName = fontMapping[selectedValue] || 'inherit';
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = convertedText.innerHTML;
        
        const legacySpans = tempDiv.querySelectorAll('.font-legacy');
        legacySpans.forEach(span => {
            span.style.fontFamily = fontName === 'inherit' ? 'inherit' : `${fontName}, Arial, sans-serif`;
        });
        
        const englishSpans = tempDiv.querySelectorAll('.font-english');
        englishSpans.forEach(span => {
            span.style.fontFamily = "'Arial', 'Calibri', sans-serif";
        });
        
        // Convert newlines to br tags for Word compatibility
        const bodyContent = tempDiv.innerHTML.replace(/\r?\n/g, '<br>');
        
        // Wrap in Microsoft Word HTML format
        const htmlDoc = `
        <html xmlns:o='urn:schemas-microsoft-com:office:office' 
              xmlns:w='urn:schemas-microsoft-com:office:word' 
              xmlns='http://www.w3.org/TR/REC-html40'>
        <head>
            <meta charset="utf-8">
            <style>
                body {
                    font-family: 'Arial', 'Calibri', sans-serif;
                    font-size: 11pt;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            ${bodyContent}
        </body>
        </html>
        `;
        
        // Export file as .doc
        const blob = new Blob(['\ufeff' + htmlDoc], { type: 'application/msword;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'converted_document.doc';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        updateStatus('📄 Formatted Word Document downloaded!', 'success');
    });

    // ---------- DOCX Advanced Formatting Conversion ----------
    function convertDocx() {
        if (!window._docxData) {
            alert('No docx document cache found.');
            return;
        }
        const toFont = targetFontSelect.value;
        updateStatus('🔄 Converting Word formatting structural fonts...', 'info');

        fetch('/convert_docx', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_b64: window._docxData, from_font: 'auto', to_font: toFont })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            const link = document.createElement('a');
            link.href = 'data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,' + data.file_b64;
            link.download = `converted_${toFont}.docx`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            updateStatus('✅ Formatted Word document conversion complete!', 'success');
        })
        .catch(err => {
            updateStatus('❌ Word conversion error', 'danger');
            alert('Conversion error: ' + err.message);
        });
    }

    // ---------- Status Helper Functions ----------
    function updateStatus(message, type = 'info') {
        let icon = '<i class="fa-solid fa-folder text-success"></i>';
        if (type === 'success') icon = '<i class="fa-solid fa-circle-check text-success"></i>';
        if (type === 'warning') icon = '<i class="fa-solid fa-triangle-exclamation text-warning"></i>';
        if (type === 'danger') icon = '<i class="fa-solid fa-circle-exclamation text-danger"></i>';
        
        statusMessage.innerHTML = `${icon} ${message}`;
    }

    function showStatus(message, type = 'info') {
        updateStatus(message, type);
        setTimeout(() => {
            updateStatus('System Ready', 'success');
        }, 5000);
    }
});