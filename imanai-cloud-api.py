#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ImanAI Cloud API - نسخه مخصوص سایت و GitHub Actions
قابلیت‌ها:
- دریافت درخواست از سایت
- پردازش با ImanAILite
- برگرداندن پاسخ JSON
"""

import os
import sys
import json
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

# ========== تنظیم مسیر ImanAILite ==========
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ImanAILite"))

# ========== Import ImanAILite ==========
IMANAI_AVAILABLE = False
try:
    from ImanAILite import ImanAILite
    IMANAI_AVAILABLE = True
    print("✅ ImanAILite loaded")
except ImportError as e:
    print(f"⚠️ ImanAILite not found: {e}")
    # نسخه جایگزین ساده
    class ImanAILite:
        def __init__(self, verbose=False):
            self.verbose = verbose
            self.knowledge = {
                'سلام': '👋 سلام! من ImanAI هستم، دستیار هوشمند شما.',
                'خوبی': '🙂 ممنون! من همیشه آماده کمک هستم.',
                'اسمت': '🤖 اسم من ImanAI هست.',
                'چه کاری میتونی': 'میتونم به سوالات مالی پاسخ بدم.',
                'موجودی صندوق': '💰 موجودی صندوق: ۱۵,۳۲۰,۰۰۰ ریال',
                'موجودی بانک': '🏦 موجودی بانک: ۸۲,۴۵۰,۰۰۰ ریال',
                'فروش امروز': '📈 فروش امروز: ۳,۲۰۰,۰۰۰ ریال',
                'راهنما': 'سوالات: سلام, موجودی صندوق, موجودی بانک, فروش امروز',
                'خداحافظ': '👋 خداحافظ!'
            }
        
        def chat(self, message):
            msg_lower = message.lower()
            for key, resp in self.knowledge.items():
                if key in msg_lower:
                    return resp
            return f'دریافت شد: {message[:100]}... (برای راهنما بگویید "راهنما")'
    
    print("⚠️ Using fallback ImanAILite")

# ========== دیتابیس ساده ==========
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imanai_cloud.db")

def init_db():
    """راه‌اندازی دیتابیس ساده"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            ai_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_value TEXT UNIQUE,
            name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # اضافه کردن کلید پیش‌فرض
    c.execute("SELECT COUNT(*) FROM api_keys")
    if c.fetchone()[0] == 0:
        default_key = f"imanai_{uuid.uuid4().hex[:16]}"
        c.execute("INSERT INTO api_keys (key_value, name) VALUES (?, ?)", (default_key, "Default API Key"))
        print(f"\n🔑 Default API Key: {default_key}\n")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_conversation(session_id: str, user_message: str, ai_response: str):
    """ذخیره مکالمه در دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO conversations (session_id, user_message, ai_response)
                 VALUES (?, ?, ?)''', (session_id, user_message[:500], ai_response[:500]))
    conn.commit()
    conn.close()

# ========== ImanAI Engine ==========

class ImanAIEngine:
    """موتور اصلی ImanAI"""
    
    def __init__(self):
        self.ai = ImanAILite(verbose=False)
        self.sessions = {}
    
    def chat(self, message: str, session_id: str = None) -> Dict:
        """پردازش پیام و برگرداندن پاسخ"""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        try:
            response = self.ai.chat(message)
            
            # ذخیره در دیتابیس
            save_conversation(session_id, message, response)
            
            return {
                'success': True,
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ خطا: {str(e)}"
            }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """تحلیل احساسات متن"""
        text_lower = text.lower()
        
        positive = ['خوب', 'عالی', 'عشق', 'ممنون', 'دوست', 'عالیه', 'خوشحال']
        negative = ['بد', 'خراب', 'اشتباه', 'مشکل', 'ناراحت', 'بدک', 'خرابه']
        
        pos_score = sum(1 for w in positive if w in text_lower)
        neg_score = sum(1 for w in negative if w in text_lower)
        
        if pos_score > neg_score:
            sentiment = 'positive'
            confidence = 0.7 + (pos_score * 0.05)
        elif neg_score > pos_score:
            sentiment = 'negative'
            confidence = 0.6 + (neg_score * 0.05)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': min(confidence, 0.99),
            'text': text[:200]
        }
    
    def verify_api_key(self, api_key: str) -> bool:
        """بررسی اعتبار API Key"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM api_keys WHERE key_value = ? AND is_active = 1", (api_key,))
        result = c.fetchone() is not None
        conn.close()
        return result
    
    def get_stats(self) -> Dict:
        """دریافت آمار"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
        total_keys = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'total_api_keys': total_keys,
            'ai_available': IMANAI_AVAILABLE,
            'status': 'online',
            'version': '2.6.0'
        }

# ========== راه‌اندازی اولیه ==========
init_db()
engine = ImanAIEngine()

# ========== Flask API (برای اجرا روی سرور) ==========
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/chat', methods=['POST'])
    def chat_endpoint():
        """دریافت پیام و برگرداندن پاسخ"""
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        api_key = request.headers.get('X-API-Key', '')
        
        # بررسی API Key (اختیاری)
        if api_key and not engine.verify_api_key(api_key):
            return jsonify({'error': 'Invalid API Key'}), 401
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        result = engine.chat(message, session_id)
        return jsonify(result)
    
    @app.route('/analyze', methods=['POST'])
    def analyze_endpoint():
        """تحلیل احساسات متن"""
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        result = engine.analyze_sentiment(text)
        return jsonify(result)
    
    @app.route('/status', methods=['GET'])
    def status_endpoint():
        """دریافت وضعیت سیستم"""
        return jsonify(engine.get_stats())
    
    @app.route('/verify-key', methods=['POST'])
    def verify_key_endpoint():
        """بررسی اعتبار API Key"""
        data = request.json
        api_key = data.get('api_key', '')
        is_valid = engine.verify_api_key(api_key)
        return jsonify({'valid': is_valid})
    
    print("✅ Flask API endpoints ready")
    
except ImportError:
    print("⚠️ Flask not installed. Run: pip install flask flask-cors")
    app = None

# ========== تابع اصلی برای GitHub Actions ==========

def process_request(action: str, data: Dict) -> Dict:
    """پردازش درخواست برای GitHub Actions"""
    
    if action == 'chat':
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        return engine.chat(message, session_id)
    
    elif action == 'analyze':
        text = data.get('text', '')
        return engine.analyze_sentiment(text)
    
    elif action == 'status':
        return engine.get_stats()
    
    else:
        return {'error': f'Unknown action: {action}', 'available': ['chat', 'analyze', 'status']}

# ========== اجرای مستقیم ==========

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ImanAI Cloud API')
    parser.add_argument('--mode', choices=['flask', 'test'], default='flask',
                       help='حالت اجرا')
    parser.add_argument('--port', type=int, default=5000,
                       help='پورت سرور (پیش‌فرض: 5000)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='هاست سرور (پیش‌فرض: 0.0.0.0)')
    
    args = parser.parse_args()
    
    if args.mode == 'flask':
        if app:
            print(f"🚀 Starting ImanAI Cloud API on http://{args.host}:{args.port}")
            print(f"   - POST /chat - ارسال پیام")
            print(f"   - POST /analyze - تحلیل احساسات")
            print(f"   - GET /status - وضعیت سیستم")
            app.run(host=args.host, port=args.port, debug=False)
        else:
            print("❌ Flask not installed. Run: pip install flask flask-cors")
    else:
        # حالت تست
        print("🧠 Testing ImanAI Cloud API")
        print("=" * 50)
        
        result = engine.chat("سلام")
        print(f"Chat: {result}")
        
        result = engine.analyze_sentiment("این برنامه خیلی عالیه!")
        print(f"Sentiment: {result}")
        
        stats = engine.get_stats()
        print(f"Stats: {stats}")
