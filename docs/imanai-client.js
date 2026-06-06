// ImanAI Client - نسخه کامل
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
                reject(new Error('زمان پاسخ به پایان رسید (30 ثانیه)'));
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
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
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
        const maxAttempts = 20;
        
        const interval = setInterval(async () => {
            attempts++;
            
            try {
                const runsRes = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/runs?event=repository_dispatch&per_page=5`);
                const runs = await runsRes.json();
                
                for (const run of (runs.workflow_runs || [])) {
                    if (run.status === 'completed') {
                        const logsRes = await fetch(run.logs_url);
                        const logText = await logsRes.text();
                        const match = logText.match(/IMANAI_RESPONSE::(.+)/);
                        
                        if (match) {
                            try {
                                const result = JSON.parse(decodeURIComponent(match[1]));
                                const pending = this.pendingRequests.get(requestId);
                                if (pending && result.request_id !== requestId) {
                                    continue;
                                }
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
                        pending.reject(new Error('پاسخی از سرور دریافت نشد'));
                    }
                }
            } catch (error) {
                console.error('خطا در بررسی پاسخ:', error);
            }
        }, 2000);
    }
    
    // ========== API های عمومی ==========
    
    async chat(message) {
        return this._call('chat', { message });
    }
    
    async train(question, answer) {
        return this._call('train', { question, answer });
    }
    
    async getStatus() {
        return this._call('status', {});
    }
}

// ایجاد نمونه سراسری
const imanai = new ImanAIClient();

// ========== توابع کمکی برای استفاده در سایت ==========

async function askImanAI(message) {
    try {
        const result = await imanai.chat(message);
        if (result.success) {
            return result.response;
        }
        return result.response || 'پاسخی دریافت نشد';
    } catch (error) {
        console.error('Error:', error);
        return `❌ خطا: ${error.message}`;
    }
}

async function teachImanAI(question, answer) {
    try {
        const result = await imanai.train(question, answer);
        if (result.success) {
            return result.message;
        }
        return `❌ ${result.error}`;
    } catch (error) {
        return `❌ خطا: ${error.message}`;
    }
}

async function checkImanAIStatus() {
    try {
        const status = await imanai.getStatus();
        return status.status === 'online';
    } catch {
        return false;
    }
}

// بررسی وضعیت در شروع
checkImanAIStatus().then(online => {
    console.log('ImanAI status:', online ? '✅ آنلاین' : '❌ آفلاین');
});
