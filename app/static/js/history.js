// History Page Functionality
class PlanktonHistory {
    constructor() {
        this.currentTab = 'chat-history';
        this.currentPage = 1;
        this.perPage = 10;
        this.deleteItemId = null;
        this.deleteType = null;
        
        this.initEventListeners();
        this.loadChatHistory();
    }
    
    initEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });
        
        // Clear history button
        document.getElementById('clearHistoryBtn').addEventListener('click', () => {
            this.openDeleteModal(null, 'all');
        });
        
        // Delete modal buttons
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
            this.confirmDelete();
        });
        document.getElementById('cancelDeleteBtn').addEventListener('click', () => {
            this.closeDeleteModal();
        });
    }
    
    switchTab(tabName) {
        this.currentTab = tabName;
        this.currentPage = 1;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        // Load appropriate history
        if (tabName === 'chat-history') {
            this.loadChatHistory();
        } else {
            this.loadAnalysisHistory();
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`/api/chat/history?page=${this.currentPage}&per_page=${this.perPage}`);
            
            if (!response.ok) {
                throw new Error('Gagal memuat riwayat chat');
            }
            
            const data = await response.json();
            this.displayChatHistory(data);
            this.displayPagination(data.pages);
            
        } catch (error) {
            this.showError('Gagal memuat riwayat chat: ' + error.message);
        }
    }
    
    async loadAnalysisHistory() {
        try {
            const response = await fetch(`/api/plant/history?page=${this.currentPage}&per_page=${this.perPage}`);
            
            if (!response.ok) {
                throw new Error('Gagal memuat riwayat analisis');
            }
            
            const data = await response.json();
            this.displayAnalysisHistory(data);
            this.displayPagination(data.pages);
            
        } catch (error) {
            this.showError('Gagal memuat riwayat analisis: ' + error.message);
        }
    }
    
    displayChatHistory(data) {
        const list = document.getElementById('chatHistoryList');
        
        if (data.data.length === 0) {
            list.innerHTML = '<p class="empty-state">Tidak ada riwayat chat</p>';
            return;
        }
        
        list.innerHTML = data.data.map(item => `
            <div class="history-item">
                <div class="history-item-header">
                    <span class="history-item-time">${new Date(item.created_at).toLocaleString('id-ID')}</span>
                    <button class="history-item-delete" onclick="deleteChatItem(${item.id})">🗑️</button>
                </div>
                <div class="history-item-message">
                    <div class="message-label">👤 Anda</div>
                    <div class="message-content" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%); border-left: 3px solid #10b981;">
                        ${this.escapeHtml(item.user_message)}
                    </div>
                </div>
                <div class="history-item-message">
                    <div class="message-label">🤖 Asisten AI</div>
                    <div class="message-content" style="border-left: 3px solid #3b82f6;">
                        ${this.parseMarkdown(item.ai_response)}
                    </div>
                </div>
                <div style="margin-top: 0.75rem; padding: 0.5rem; background: #f0fdf4; border-radius: 0.375rem; font-size: 0.8rem; color: #15803d;">
                    📌 Topik: <strong>${item.plant_topic || 'Umum'}</strong>
                </div>
            </div>
        `).join('');
    }
    
    displayAnalysisHistory(data) {
        const list = document.getElementById('analysisHistoryList');
        
        if (data.data.length === 0) {
            list.innerHTML = '<p class="empty-state">Tidak ada riwayat analisis</p>';
            return;
        }
        
        list.innerHTML = data.data.map(item => {
            let analysisContent = '';
            
            // Parse analysis_result if it exists
            if (item.analysis_result) {
                const result = item.analysis_result;
                
                // Health status
                if (result.health && result.health.is_healthy) {
                    const status = result.health.is_healthy.status ? '✅ Sehat' : '⚠️ Ada masalah';
                    analysisContent += `<div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; border-radius: 0.25rem; color: #000;">
                        <strong>Status Kesehatan:</strong> ${status}
                    </div>`;
                }
                
                // Diseases
                if (result.health && result.health.diseases && result.health.diseases.suggestions.length > 0) {
                    analysisContent += '<div style="margin: 0.75rem 0; color: #000;"><strong>🦠 Penyakit Terdeteksi:</strong>';
                    result.health.diseases.suggestions.forEach(disease => {
                        analysisContent += `<div style="margin-left: 1rem; margin-top: 0.25rem; color: #000;">
                            • ${disease.name} (${(disease.probability * 100).toFixed(1)}%)
                        </div>`;
                    });
                    analysisContent += '</div>';
                }
                
                // Pests
                if (result.health && result.health.pests && result.health.pests.suggestions.length > 0) {
                    analysisContent += '<div style="margin: 0.75rem 0;"><strong>🐛 Hama Terdeteksi:</strong>';
                    result.health.pests.suggestions.forEach(pest => {
                        analysisContent += `<div style="margin-left: 1rem; margin-top: 0.25rem;">
                            • ${pest.name} (${(pest.probability * 100).toFixed(1)}%)
                        </div>`;
                    });
                    analysisContent += '</div>';
                }
                
                // Nutrient deficiency
                if (result.health && result.health.nutrient_deficiency && result.health.nutrient_deficiency.suggestions.length > 0) {
                    analysisContent += '<div style="margin: 0.75rem 0;"><strong>📊 Defisiensi Nutrisi:</strong>';
                    result.health.nutrient_deficiency.suggestions.forEach(def => {
                        analysisContent += `<div style="margin-left: 1rem; margin-top: 0.25rem;">
                            • ${def.nutrient} (${(def.probability * 100).toFixed(1)}%)
                        </div>`;
                    });
                    analysisContent += '</div>';
                }
            }
            
            // AI Recommendations
            let recommendationsContent = '';
            if (item.ai_recommendations) {
                recommendationsContent = `<div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); border-left: 4px solid #667eea; border-radius: 0.5rem;">
                    <div style="margin-bottom: 0.5rem; font-size: 1.05em; font-weight: 600; color: #667eea;">💡 Rekomendasi Penanganan:</div>
                    <div style="color: #fff; line-height: 1.6;">
                        ${this.parseMarkdown(item.ai_recommendations)}
                    </div>
                </div>`;
            }
            
            return `
                <div class="history-item">
                    <div class="history-item-header">
                        <span class="history-item-time">${new Date(item.created_at).toLocaleString('id-ID')}</span>
                        <button class="history-item-delete" onclick="deleteAnalysisItem(${item.id})">🗑️</button>
                    </div>
                    <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                        <img src="${item.image_url}" alt="Analysis" style="width: 120px; height: 120px; object-fit: cover; border-radius: 0.5rem; border: 2px solid #e2e8f0;">
                        <div style="flex: 1;">
                            <div class="history-item-message">
                                <div class="message-label">Tanaman Terdeteksi</div>
                                <div class="message-content">
                                    <div><strong style="font-size: 1.1em;">${this.escapeHtml(item.plant_name)}</strong></div>
                                    <div style="font-size: 0.9em; color: #666; margin-top: 0.25rem;">
                                        🇮🇩 ${this.escapeHtml(item.plant_name_id || item.plant_name)}<br>
                                        🇬🇧 ${this.escapeHtml(item.plant_name_en || item.plant_name)}
                                    </div>
                                </div>
                            </div>
                            <div class="history-item-message">
                                <div class="message-label">Keyakinan</div>
                                <div class="message-content">
                                    <div style="display: inline-block; background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%); padding: 0.5rem 1rem; border-radius: 0.5rem;">
                                        ${Math.round(item.confidence)}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ${analysisContent ? `<div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; font-size: 0.95em;">${analysisContent}</div>` : ''}
                    ${recommendationsContent}
                </div>
            `;
        }).join('');
    }
    
    displayPagination(totalPages) {
        const pagination = document.getElementById('pagination');
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        if (this.currentPage > 1) {
            html += `<button class="page-btn" onclick="history.goToPage(${this.currentPage - 1})">← Sebelumnya</button>`;
        }
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                html += `<button class="page-btn active">${i}</button>`;
            } else {
                html += `<button class="page-btn" onclick="history.goToPage(${i})">${i}</button>`;
            }
        }
        
        if (this.currentPage < totalPages) {
            html += `<button class="page-btn" onclick="history.goToPage(${this.currentPage + 1})">Selanjutnya →</button>`;
        }
        
        pagination.innerHTML = html;
    }
    
    goToPage(page) {
        this.currentPage = page;
        if (this.currentTab === 'chat-history') {
            this.loadChatHistory();
        } else {
            this.loadAnalysisHistory();
        }
        window.scrollTo(0, 0);
    }
    
    deleteChatItem(id) {
        console.log('Delete chat item:', id);
        this.deleteItemId = id;
        this.deleteType = 'chat';
        this.showDeleteModal();
    }
    
    deleteAnalysisItem(id) {
        console.log('Delete analysis item:', id);
        this.deleteItemId = id;
        this.deleteType = 'analysis';
        this.showDeleteModal();
    }
    
    showDeleteModal() {
        console.log('Show modal - Type:', this.deleteType, 'ID:', this.deleteItemId);
        document.getElementById('deleteModal').classList.add('active');
    }
    
    openDeleteModal(itemId, type) {
        // For "Hapus Semua" button - this version accepts parameters
        console.log('Open modal with params - Type:', type, 'ID:', itemId);
        if (type !== undefined) {
            this.deleteType = type;
        }
        if (itemId !== null && itemId !== undefined) {
            this.deleteItemId = itemId;
        }
        document.getElementById('deleteModal').classList.add('active');
    }
    
    closeDeleteModal() {
        document.getElementById('deleteModal').classList.remove('active');
        this.deleteItemId = null;
        this.deleteType = null;
    }
    
    async confirmDelete() {
        try {
            let url = '';
            let method = 'POST';
            
            console.log('Delete Type:', this.deleteType);
            console.log('Current Tab:', this.currentTab);
            console.log('Delete Item ID:', this.deleteItemId);
            
            if (this.deleteType === 'all') {
                // Delete all depends on current tab
                if (this.currentTab === 'chat-history') {
                    url = '/api/chat/history/clear';
                    method = 'POST';
                } else if (this.currentTab === 'plant-analysis') {
                    url = '/api/plant/history/clear';
                    method = 'POST';
                } else {
                    throw new Error('Tab tidak valid: ' + this.currentTab);
                }
            } else if (this.deleteType === 'chat') {
                url = `/api/chat/history/${this.deleteItemId}`;
                method = 'DELETE';
            } else if (this.deleteType === 'analysis') {
                url = `/api/plant/history/${this.deleteItemId}`;
                method = 'DELETE';
            }
            
            console.log('Request:', method, url);
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.status === 204 || response.status === 200) {
                // Success - reload the current history
                if (this.currentTab === 'chat-history') {
                    this.loadChatHistory();
                } else {
                    this.loadAnalysisHistory();
                }
                this.closeDeleteModal();
            } else if (response.status === 404) {
                alert('Item tidak ditemukan');
                if (this.currentTab === 'chat-history') {
                    this.loadChatHistory();
                } else {
                    this.loadAnalysisHistory();
                }
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Gagal menghapus item');
            }
            
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
    
    showError(message) {
        const list = document.getElementById('chatHistoryList');
        list.innerHTML = `<p class="empty-state" style="color: var(--danger);">${message}</p>`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    parseMarkdown(text) {
        // First, preserve existing <br> and HTML tags
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
        
        // Escape HTML
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
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        // Lists - unordered
        html = html.replace(/^\- (.*?)$/gm, '<li style="margin-left: 20px;">$1</li>');
        html = html.replace(/(<li[\s\S]*?<\/li>)/g, '<ul style="margin: 10px 0; padding-left: 0;">$1</ul>');
        
        // Lists - ordered
        html = html.replace(/^\d+\)\s(.*?)$/gm, '<li style="margin-left: 20px;">$1</li>');
        html = html.replace(/^(\d+)\.\s(.*?)$/gm, '<li style="margin-left: 20px;">$2</li>');
        
        // Inline code
        html = html.replace(/`(.*?)`/g, '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em;">$1</code>');
        
        // Restore code blocks
        for (const [placeholder, code] of Object.entries(codePlaceholders)) {
            const cleanCode = code.replace(/```/g, '').trim();
            const styledCode = `<pre style="background: #2d3748; color: #e2e8f0; padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 0.75rem 0; font-size: 0.85em; line-height: 1.4;"><code>${cleanCode}</code></pre>`;
            html = html.replace(placeholder, styledCode);
        }
        
        return html;
    }
}

// Initialize when document is ready
let history;
document.addEventListener('DOMContentLoaded', () => {
    history = new PlanktonHistory();
});

// Global functions for onclick handlers
function goToPage(page) {
    history.goToPage(page);
}

function deleteChatItem(id) {
    history.deleteChatItem(id);
}

function deleteAnalysisItem(id) {
    history.deleteAnalysisItem(id);
}
