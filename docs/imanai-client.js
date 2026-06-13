// imanai-client.js - نسخه کامل برای پنل کاربری

const GITHUB_REPO = "neonpresents01-beep/ImanAI";
const GITHUB_TOKEN = "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";

let currentApiKey = localStorage.getItem('imanai_api_key');

async function callAPI(action, payload = {}) {
    const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
        method: 'POST',
        headers: { 
            'Authorization': `Bearer ${GITHUB_TOKEN}`, 
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify({ 
            event_type: action, 
            client_payload: { ...payload, api_key: currentApiKey || '' } 
        })
    });
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    // منتظر ماندن برای اجرای workflow
    for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 3000));
        
        const runs = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/runs?per_page=5&event=repository_dispatch`);
        const data = await runs.json();
        
        for (const run of (data.workflow_runs || [])) {
            if (run.status === 'completed') {
                const logs = await fetch(run.logs_url);
                const text = await logs.text();
                const match = text.match(/API_RESPONSE::(.+)/);
                if (match) {
                    return JSON.parse(decodeURIComponent(match[1]));
                }
            }
        }
    }
    throw new Error('Timeout waiting for response');
}

async function register() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const plan = document.getElementById('plan').value;
    const resultDiv = document.getElementById('registerResult');
    
    if (!name || !email) {
        resultDiv.innerHTML = '<div class="result error">❌ نام و ایمیل الزامی است</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div>⏳ در حال ثبت‌نام...</div>';
    
    try {
        const result = await callAPI('register', { customer_name: name, customer_email: email, plan });
        if (result.success) {
            currentApiKey = result.api_key;
            localStorage.setItem('imanai_api_key', currentApiKey);
            resultDiv.innerHTML = '<div class="result success">✅ ثبت‌نام موفق! API Key ذخیره شد.</div>';
            setTimeout(() => location.reload(), 1500);
        } else {
            resultDiv.innerHTML = `<div class="result error">❌ ${result.error}</div>`;
        }
    } catch(e) {
        resultDiv.innerHTML = `<div class="result error">❌ خطا: ${e.message}</div>`;
    }
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    
    const messages = document.getElementById('chatMessages');
    messages.innerHTML += `<div style="margin: 5px 0; padding: 8px; background: #2563eb; border-radius: 12px; text-align: right;">👤 شما: ${msg}</div>`;
    input.value = '';
    
    messages.innerHTML += `<div style="margin: 5px 0; padding: 8px; background: #1e293b; border-radius: 12px;">🤖 در حال فکر کردن...</div>`;
    messages.scrollTop = messages.scrollHeight;
    
    try {
        const result = await callAPI('chat', { message: msg });
        messages.removeChild(messages.lastChild);
        
        if (result.success) {
            messages.innerHTML += `<div style="margin: 5px 0; padding: 8px; background: #1e293b; border-radius: 12px;">🤖 ImanAI: ${result.response}</div>`;
            document.getElementById('creditsDisplay').innerHTML = result.remaining_credits;
        } else {
            messages.innerHTML += `<div style="margin: 5px 0; padding: 8px; background: #ef4444; border-radius: 12px;">❌ ${result.error}</div>`;
        }
    } catch(e) {
        messages.removeChild(messages.lastChild);
        messages.innerHTML += `<div style="margin: 5px 0; padding: 8px; background: #ef4444; border-radius: 12px;">❌ خطا: ${e.message}</div>`;
    }
    messages.scrollTop = messages.scrollHeight;
}

async function loadDashboard() {
    if (!currentApiKey) return;
    
    try {
        const result = await callAPI('balance', {});
        if (result.success) {
            document.getElementById('creditsDisplay').innerHTML = result.credits;
            document.getElementById('apiKeyDisplay').innerHTML = currentApiKey;
            
            // نمایش پلن
            const planDisplay = document.getElementById('planDisplay');
            if (planDisplay) planDisplay.innerHTML = result.plan;
        }
    } catch(e) {
        console.error(e);
    }
}

function logout() {
    localStorage.removeItem('imanai_api_key');
    location.reload();
}

function copyApiKey() {
    navigator.clipboard.writeText(currentApiKey);
    alert('✅ API Key کپی شد!');
}

function updateUI() {
    if (currentApiKey) {
        document.getElementById('registerBox').style.display = 'none';
        document.getElementById('dashboardBox').style.display = 'block';
        loadDashboard();
    } else {
        document.getElementById('registerBox').style.display = 'block';
        document.getElementById('dashboardBox').style.display = 'none';
    }
}

// اجرا در هنگام بارگذاری
document.addEventListener('DOMContentLoaded', updateUI);
