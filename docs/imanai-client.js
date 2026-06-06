// ImanAI Client - نسخه کامل با تمام توابع
const GITHUB_REPO = "neonpresents01-beep/ImanAI";
const GITHUB_TOKEN = "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";

class ImanAIClient {
    constructor(apiKey = null) {
        this.apiKey = apiKey || localStorage.getItem('imanai_api_key');
        this.pending = new Map();
    }
    
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        if (apiKey) {
            localStorage.setItem('imanai_api_key', apiKey);
        } else {
            localStorage.removeItem('imanai_api_key');
        }
    }
    
    async _call(action, payload = {}) {
        const requestId = Date.now().toString();
        
        return new Promise(async (resolve, reject) => {
            const timeout = setTimeout(() => {
                this.pending.delete(requestId);
                reject(new Error('Timeout (30s)'));
            }, 30000);
            
            this.pending.set(requestId, { resolve, reject, timeout });
            
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
                        client_payload: { 
                            ...payload, 
                            request_id: requestId,
                            api_key: this.apiKey || ''
                        }
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                this._poll(requestId);
            } catch (error) {
                clearTimeout(timeout);
                this.pending.delete(requestId);
                reject(error);
            }
        });
    }
    
    async _poll(requestId) {
        let attempts = 0;
        const maxAttempts = 20;
        
        const interval = setInterval(async () => {
            attempts++;
            try {
                const runs = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/runs?event=repository_dispatch&per_page=5`);
                const data = await runs.json();
                
                for (const run of (data.workflow_runs || [])) {
                    if (run.status === 'completed') {
                        const logs = await fetch(run.logs_url);
                        const text = await logs.text();
                        const match = text.match(/API_RESPONSE::(.+)/);
                        if (match) {
                            try {
                                const result = JSON.parse(decodeURIComponent(match[1]));
                                const pending = this.pending.get(requestId);
                                if (pending) {
                                    clearInterval(interval);
                                    clearTimeout(pending.timeout);
                                    this.pending.delete(requestId);
                                    pending.resolve(result);
                                }
                                return;
                            } catch(e) {
                                console.error('Parse error:', e);
                            }
                        }
                    }
                }
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    const pending = this.pending.get(requestId);
                    if (pending) {
                        this.pending.delete(requestId);
                        pending.reject(new Error('No response from server'));
                    }
                }
            } catch (e) {
                console.error('Poll error:', e);
            }
        }, 2000);
    }
    
    // ========== API ها ==========
    
    async register(name, email, plan = 'free') {
        return this._call('register', { 
            customer_name: name, 
            customer_email: email, 
            plan: plan 
        });
    }
    
    async chat(message) {
        if (!this.apiKey) {
            return { success: false, error: 'لطفاً ابتدا ثبت‌نام کنید', code: 'NOT_REGISTERED' };
        }
        return this._call('chat', { message });
    }
    
    async train(question, answer) {
        if (!this.apiKey) {
            return { success: false, error: 'لطفاً ابتدا ثبت‌نام کنید', code: 'NOT_REGISTERED' };
        }
        return this._call('train', { question, answer });
    }
    
    async getBalance() {
        if (!this.apiKey) {
            return { success: false, error: 'لطفاً ابتدا ثبت‌نام کنید' };
        }
        return this._call('balance', {});
    }
    
    async getPricing() {
        return this._call('pricing', {});
    }
    
    async getStatus() {
        return this._call('status', {});
    }
}

// ========== ایجاد نمونه سراسری ==========
let imanai = new ImanAIClient();

// ========== توابع کمکی برای استفاده در سایت ==========

async function registerUser(name, email, plan) {
    try {
        const result = await imanai.register(name, email, plan);
        if (result.success) {
            imanai.setApiKey(result.api_key);
            return { success: true, api_key: result.api_key, credits: result.credits, message: result.message };
        }
        return { success: false, error: result.error };
    } catch (error) {
        console.error('Register error:', error);
        return { success: false, error: error.message };
    }
}

async function askImanAI(message) {
    if (!imanai.apiKey) {
        return '❌ لطفاً ابتدا در پنل کاربری ثبت‌نام کنید';
    }
    try {
        const result = await imanai.chat(message);
        if (result.success) {
            return result.response;
        }
        if (result.code === 'INSUFFICIENT_CREDITS') {
            return '❌ اعتبار شما تمام شده است. لطفاً شارژ کنید.';
        }
        return `❌ خطا: ${result.error || 'مشخص نیست'}`;
    } catch (error) {
        console.error('Chat error:', error);
        return `❌ خطا: ${error.message}`;
    }
}

async function teachImanAI(question, answer) {
    if (!imanai.apiKey) {
        return '❌ لطفاً ابتدا در پنل کاربری ثبت‌نام کنید';
    }
    try {
        const result = await imanai.train(question, answer);
        if (result.success) {
            return `✅ ${result.message || 'آموزش با موفقیت انجام شد!'}`;
        }
        return `❌ ${result.error || 'خطا در آموزش'}`;
    } catch (error) {
        return `❌ خطا: ${error.message}`;
    }
}

async function getUserBalance() {
    if (!imanai.apiKey) return null;
    try {
        return await imanai.getBalance();
    } catch (error) {
        console.error('Balance error:', error);
        return null;
    }
}

// توابع کمکی دیگر
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    alert('✅ کپی شد!');
}

// بررسی وضعیت در شروع
async function checkStatus() {
    try {
        const status = await imanai.getStatus();
        console.log('ImanAI Status:', status);
    } catch(e) {
        console.error('Status check failed:', e);
    }
}

checkStatus();    }
    
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
