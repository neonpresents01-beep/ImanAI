// imanai-client.js - برای استفاده در imanai.ir
const GITHUB_REPO = "neonpresents01-beep/ImanAI";
const GITHUB_TOKEN = "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";

class ImanAIClient {
    constructor() {
        this.pendingRequests = new Map();
    }
    
    async _call(action, payload = {}) {
        const requestId = Date.now().toString();
        
        return new Promise(async (resolve, reject) => {
            const timeout = setTimeout(() => {
                this.pendingRequests.delete(requestId);
                reject(new Error('Timeout (30s)'));
            }, 30000);
            
            this.pendingRequests.set(requestId, { resolve, reject, timeout });
            
            try {
                const response = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${GITHUB_TOKEN}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        event_type: action,
                        client_payload: { ...payload, request_id: requestId }
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                this._pollResponse(requestId);
                
            } catch (error) {
                clearTimeout(timeout);
                this.pendingRequests.delete(requestId);
                reject(error);
            }
        });
    }
    
    async _pollResponse(requestId) {
        let attempts = 0;
        const maxAttempts = 15;
        
        const interval = setInterval(async () => {
            attempts++;
            
            try {
                const runs = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/runs?event=repository_dispatch&per_page=3`);
                const data = await runs.json();
                
                for (const run of (data.workflow_runs || [])) {
                    if (run.status === 'completed') {
                        const logs = await fetch(run.logs_url);
                        const logText = await logs.text();
                        const match = logText.match(/IMANAI_RESPONSE::(.+)/);
                        
                        if (match) {
                            try {
                                const result = JSON.parse(decodeURIComponent(match[1]));
                                const pending = this.pendingRequests.get(requestId);
                                if (pending) {
                                    clearInterval(interval);
                                    clearTimeout(pending.timeout);
                                    this.pendingRequests.delete(requestId);
                                    pending.resolve(result);
                                }
                                return;
                            } catch(e) {}
                        }
                    }
                }
                
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    const pending = this.pendingRequests.get(requestId);
                    if (pending) {
                        this.pendingRequests.delete(requestId);
                        pending.reject(new Error('No response'));
                    }
                }
            } catch (error) {
                console.error('Poll error:', error);
            }
        }, 2000);
    }
    
    async chat(message) {
        return this._call('chat', { message });
    }
    
    async analyze(text) {
        return this._call('analyze', { text });
    }
    
    async getStatus() {
        return this._call('status', {});
    }
}

// ایجاد نمونه
const imanai = new ImanAIClient();

// تابع برای استفاده در سایت
async function askImanAI(message) {
    try {
        const result = await imanai.chat(message);
        if (result.response) {
            return result.response;
        }
        return 'متاسفانه پاسخی دریافت نشد.';
    } catch (error) {
        console.error('Error:', error);
        return `❌ خطا: ${error.message}`;
    }
}

// تابع برای نمایش در صفحه
async function sendToImanAI() {
    const input = document.getElementById('ai-input');
    const output = document.getElementById('ai-output');
    
    if (!input || !input.value.trim()) return;
    
    const userMessage = input.value;
    
    if (output) {
        output.innerHTML += `<div class="user-msg">👤 شما: ${userMessage}</div>`;
    }
    
    const response = await askImanAI(userMessage);
    
    if (output) {
        output.innerHTML += `<div class="ai-msg">🤖 ImanAI: ${response}</div>`;
        output.scrollTop = output.scrollHeight;
    }
    
    if (input) input.value = '';
}

// بررسی وضعیت
async function checkAIStatus() {
    try {
        const status = await imanai.getStatus();
        console.log('ImanAI Status:', status);
        return status.status === 'online';
    } catch {
        return false;
    }
}

// اجرای خودکار بررسی وضعیت
checkAIStatus();
