// Main Chat Functionality
class PlanktonChat {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.loading = document.getElementById('loading');
        this.uploadArea = document.getElementById('uploadArea');
        this.imageInput = document.getElementById('imageInput');
        this.analysisResult = document.getElementById('analysisResult');
        this.plantTopic = document.getElementById('plantTopic');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.imageInput.click());
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.style.backgroundColor = 'rgba(16, 185, 129, 0.15)';
        });
        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.style.backgroundColor = '';
        });
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.style.backgroundColor = '';
            if (e.dataTransfer.files.length > 0) {
                this.analyzePlant(e.dataTransfer.files[0]);
            }
        });
        
        this.imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.analyzePlant(e.target.files[0]);
            }
        });
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        this.messageInput.value = '';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show loading in chat
        this.showLoading('Sedang berpikir...');
        this.sendBtn.disabled = true;
        
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    plant_topic: this.plantTopic.value
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Gagal mengirim pesan');
            }
            
            const data = await response.json();
            this.hideLoading();
            this.addMessage(data.ai_response, 'bot');
            
        } catch (error) {
            this.hideLoading();
            this.addMessage('Maaf, terjadi kesalahan: ' + error.message, 'bot');
        } finally {
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }
    
    showLoading(text = 'Sedang berpikir...') {
        document.getElementById('loadingText').textContent = text;
        this.loading.style.display = 'flex';
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const p = document.createElement('p');
        // Simple markdown to HTML conversion
        let html = this.parseMarkdown(text);
        p.innerHTML = html;
        
        messageDiv.appendChild(p);
        
        // Insert before loading element
        this.messagesContainer.insertBefore(messageDiv, this.loading);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    parseMarkdown(text) {
        // First, preserve existing <br> and HTML tags by replacing them temporarily
        const brPlaceholder = '___BR_TAG___';
        text = text.replace(/<br\s*\/?>/gi, brPlaceholder);
        
        // Preserve code blocks temporarily
        const codePlaceholders = {};
        let codeIndex = 0;
        text = text.replace(/```[\s\S]*?```/g, function(match) {
            const placeholder = `___CODE_${codeIndex}___`;
            codePlaceholders[placeholder] = match;
            codeIndex++;
            return placeholder;
        });
        
        // Preserve tables temporarily and convert to HTML tables
        const tablePlaceholders = {};
        let tableIndex = 0;
        
        // Match markdown tables
        text = text.replace(/(\|[^\n]+\|\n)(\|[-:\s|]+\|\n)((?:\|[^\n]+\|\n?)+)/g, function(match, header, separator, body) {
            const placeholder = `___TABLE_${tableIndex}___`;
            
            // Parse header
            const headerCells = header.split('|').filter(cell => cell.trim()).map(cell => cell.trim());
            
            // Parse body rows
            const bodyRows = body.trim().split('\n').map(row => {
                return row.split('|').filter(cell => cell.trim()).map(cell => cell.trim());
            });
            
            // Build HTML table wrapped in scrollable container
            let tableHtml = '<div class="table-wrapper" style="overflow-x: auto; max-width: 100%; margin: 0.75rem 0;">';
            tableHtml += '<table style="min-width: 400px;">';
            tableHtml += '<thead><tr>';
            headerCells.forEach(cell => {
                // Restore BR tags and bold inside header cells
                let cellContent = cell.replace(/___BR_TAG___/g, '<br>');
                cellContent = cellContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                tableHtml += `<th>${cellContent}</th>`;
            });
            tableHtml += '</tr></thead>';
            tableHtml += '<tbody>';
            bodyRows.forEach(row => {
                tableHtml += '<tr>';
                row.forEach(cell => {
                    // Restore BR tags and bold inside body cells
                    let cellContent = cell.replace(/___BR_TAG___/g, '<br>');
                    cellContent = cellContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    tableHtml += `<td>${cellContent}</td>`;
                });
                tableHtml += '</tr>';
            });
            tableHtml += '</tbody></table>';
            tableHtml += '</div>';
            
            tablePlaceholders[placeholder] = tableHtml;
            tableIndex++;
            return placeholder;
        });
        
        // Escape HTML (except placeholders)
        let html = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Restore <br> tags
        html = html.replace(new RegExp(brPlaceholder, 'g'), '<br>');
        
        // Bold **text** -> <strong>text</strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic *text* -> <em>text</em>
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Headers
        html = html.replace(/^### (.*?)$/gm, '<h5>$1</h5>');
        html = html.replace(/^## (.*?)$/gm, '<h4>$1</h4>');
        html = html.replace(/^# (.*?)$/gm, '<h3>$1</h3>');
        
        // Line breaks - convert \n to <br> (but keep existing <br>)
        html = html.replace(/\n/g, '<br>');
        
        // Lists - unordered (before ordered to avoid conflicts)
        html = html.replace(/^\- (.*?)$/gm, '<li style="margin-left: 20px;">$1</li>');
        html = html.replace(/(<li[\s\S]*?<\/li>)/g, '<ul style="margin: 10px 0; padding-left: 0;">$1</ul>');
        
        // Lists - ordered
        html = html.replace(/^\d+\)\s(.*?)$/gm, '<li style="margin-left: 20px;">$1</li>');
        html = html.replace(/^(\d+)\.\s(.*?)$/gm, '<li style="margin-left: 20px;">$2</li>');
        
        // Inline code
        html = html.replace(/`(.*?)`/g, '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em;">$1</code>');
        
        // Restore code blocks with better styling
        for (const [placeholder, code] of Object.entries(codePlaceholders)) {
            const cleanCode = code.replace(/```/g, '').trim();
            const styledCode = `<pre style="background: #2d3748; color: #e2e8f0; padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 0.75rem 0; font-size: 0.85em; line-height: 1.4;"><code>${cleanCode}</code></pre>`;
            html = html.replace(placeholder, styledCode);
        }
        
        // Restore tables
        for (const [placeholder, table] of Object.entries(tablePlaceholders)) {
            html = html.replace(placeholder, table);
        }
        
        // Emojis at start of lines
        html = html.replace(/^([\p{Emoji}]+ )/gmu, '<span style="font-size: 1.2em; font-weight: 500;">$1</span>');
        
        return html;
    }
    
    async analyzePlant(file) {
        if (!file.type.startsWith('image/')) {
            alert('Harap pilih file gambar');
            return;
        }
        
        const formData = new FormData();
        formData.append('image', file);
        
        this.showLoading('🔍 Menganalisis tanaman...');
        
        try {
            const response = await fetch('/api/plant/analyze', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                const errorMsg = error.message || error.error || 'Gagal menganalisis tanaman';
                
                // Show error in chat
                this.hideLoading();
                this.addMessage(`❌ Error: ${errorMsg}`, 'bot');
                throw new Error(errorMsg);
            }
            
            const data = await response.json();
            this.hideLoading();
            this.displayAnalysisResult(data);
            
        } catch (error) {
            this.hideLoading();
            if (!error.message.includes('Error:')) {
                this.addMessage(`❌ ${error.message}`, 'bot');
            }
        } finally {
            this.imageInput.value = '';
        }
    }
    
    displayAnalysisResult(data) {
        // Show compact analysis in upload bar
        document.getElementById('analysisImageCompact').src = data.image_url;
        document.getElementById('plantNameCompact').textContent = data.plant_name;
        document.getElementById('confidenceCompact').textContent = Math.round(data.confidence);
        document.getElementById('analysisResultCompact').style.display = 'flex';
        document.getElementById('uploadText').style.display = 'none';
        
        // Also keep hidden full analysis for reference
        document.getElementById('analysisImage').src = data.image_url;
        document.getElementById('plantName').textContent = data.plant_name;
        document.getElementById('confidence').textContent = Math.round(data.confidence);
        
        // Build analysis message with health info and translation
        let message = `🌿 **${data.plant_name}**`;
        
        // Add translations if available
        if (data.plant_name_id && data.plant_name_id !== data.plant_name) {
            message += `\n🇮🇩 Indonesia: **${data.plant_name_id}**`;
        }
        if (data.plant_name_en && data.plant_name_en !== data.plant_name) {
            message += `\n🇬🇧 English: **${data.plant_name_en}**`;
        }
        
        message += `\nKeyakinan: ${Math.round(data.confidence)}%\n`;
        
        // Add health assessment if available
        if (data.health) {
            const health = data.health;
            
            // Health status
            if (health.is_healthy) {
                const status = health.is_healthy.status ? '✅ Sehat' : '⚠️ Ada masalah';
                message += `\n**Status Kesehatan**: ${status}`;
            }
            
            // Diseases
            if (health.diseases && health.diseases.suggestions.length > 0) {
                message += '\n\n🦠 **Penyakit Terdeteksi**:';
                health.diseases.suggestions.forEach(disease => {
                    message += `\n• **${disease.name}** (${(disease.probability * 100).toFixed(1)}%)`;
                    if (disease.description) {
                        message += `\n  Deskripsi: ${disease.description}`;
                    }
                    if (disease.treatment && typeof disease.treatment === 'object') {
                        if (disease.treatment.description) {
                            message += `\n  Penanganan: ${disease.treatment.description}`;
                        }
                        if (disease.treatment.steps && Array.isArray(disease.treatment.steps)) {
                            message += '\n  Langkah penanganan:';
                            disease.treatment.steps.slice(0, 3).forEach((step, idx) => {
                                message += `\n    ${idx + 1}. ${step}`;
                            });
                        }
                    }
                });
            }
            
            // Pests
            if (health.pests && health.pests.suggestions.length > 0) {
                message += '\n\n🐛 **Hama Terdeteksi**:';
                health.pests.suggestions.forEach(pest => {
                    message += `\n• **${pest.name}** (${(pest.probability * 100).toFixed(1)}%)`;
                    if (pest.description) {
                        message += `\n  Deskripsi: ${pest.description}`;
                    }
                });
            }
            
            // Nutrient deficiency
            if (health.nutrient_deficiency && health.nutrient_deficiency.suggestions.length > 0) {
                message += '\n\n📊 **Defisiensi Nutrisi**:';
                health.nutrient_deficiency.suggestions.forEach(def => {
                    message += `\n• **${def.nutrient}** (${(def.probability * 100).toFixed(1)}%)`;
                    if (def.symptoms && Array.isArray(def.symptoms) && def.symptoms.length > 0) {
                        message += '\n  Gejala:';
                        def.symptoms.slice(0, 3).forEach(symptom => {
                            message += `\n    - ${symptom}`;
                        });
                    }
                    if (def.treatment && Array.isArray(def.treatment) && def.treatment.length > 0) {
                        message += '\n  Penanganan:';
                        def.treatment.slice(0, 3).forEach(treat => {
                            message += `\n    - ${treat}`;
                        });
                    }
                });
            }
        }
        
        message += '\n\nKeterangan lebih lanjut tentang tanaman ini.';
        this.addMessage(message, 'bot');
        
        // If there are health issues, get AI recommendations
        if (data.health && (data.health.diseases?.suggestions?.length > 0 || data.health.pests?.suggestions?.length > 0)) {
            this.getHealthAdvice(data.plant_name, data.health);
        }
    }
    
    async getHealthAdvice(plantName, health) {
        try {
            const diseases = health.diseases?.suggestions || [];
            const pests = health.pests?.suggestions || [];
            
            if (diseases.length === 0 && pests.length === 0) return;
            
            const response = await fetch('/api/plant/health-advice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plant_name: plantName,
                    diseases: diseases,
                    pests: pests
                })
            });
            
            if (!response.ok) {
                console.error('Health advice error:', response.status);
                return;
            }
            
            const data = await response.json();
            
            // Display AI recommendations
            let adviceMessage = '💡 **Rekomendasi Penanganan**:\n\n' + data.advice;
            this.addMessage(adviceMessage, 'bot');
            
        } catch (error) {
            console.error('Error getting health advice:', error);
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new PlanktonChat();
});
