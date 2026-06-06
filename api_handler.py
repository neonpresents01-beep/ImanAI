# api_handler.py - فایل اصلی پردازش API
import json
import urllib.parse
import os
import hashlib
import uuid
import time

USERS_FILE = "users.json"
KNOWLEDGE_FILE = "knowledge.json"

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_knowledge():
    default = {'سلام': '👋 سلام! من ImanAI هستم.'}
    try:
        with open(KNOWLEDGE_FILE, 'r') as f:
            saved = json.load(f)
            default.update(saved)
    except:
        pass
    return default

def save_knowledge(knowledge):
    with open(KNOWLEDGE_FILE, 'w') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key():
    return f"imanai_{uuid.uuid4().hex[:16]}"

def main():
    action = os.environ.get('ACTION', '')
    api_key = os.environ.get('API_KEY', '')
    name = os.environ.get('USER_NAME', '')
    email = os.environ.get('USER_EMAIL', '')
    plan = os.environ.get('USER_PLAN', 'free')
    message = os.environ.get('USER_MESSAGE', '')
    question = os.environ.get('TRAIN_QUESTION', '')
    answer = os.environ.get('TRAIN_ANSWER', '')

    users = load_users()
    knowledge = load_knowledge()
    result = {}

    if action == 'register':
        new_key = generate_api_key()
        hashed = hash_key(new_key)
        users[hashed] = {
            'name': name,
            'email': email,
            'plan': plan,
            'credits': 10000,
            'created_at': time.time()
        }
        save_users(users)
        result = {'success': True, 'api_key': new_key, 'credits': 10000, 'plan': plan}

    elif action == 'chat':
        if not api_key:
            result = {'success': False, 'error': 'API Key required'}
        else:
            hashed = hash_key(api_key)
            if hashed not in users:
                result = {'success': False, 'error': 'Invalid API Key'}
            elif users[hashed]['credits'] <= 0:
                result = {'success': False, 'error': 'Insufficient credits'}
            else:
                users[hashed]['credits'] -= 1
                save_users(users)
                msg_lower = message.lower()
                response = None
                for key, resp in knowledge.items():
                    if key in msg_lower:
                        response = resp
                        break
                if not response:
                    response = f'دریافت شد: {message[:100]}...'
                result = {'success': True, 'response': response, 'remaining_credits': users[hashed]['credits']}

    elif action == 'balance':
        if not api_key:
            result = {'success': False, 'error': 'API Key required'}
        else:
            hashed = hash_key(api_key)
            if hashed not in users:
                result = {'success': False, 'error': 'Invalid API Key'}
            else:
                result = {'success': True, 'credits': users[hashed]['credits'], 'plan': users[hashed]['plan']}

    else:
        result = {'error': f'Unknown action: {action}'}

    encoded = urllib.parse.quote(json.dumps(result))
    print(f'API_RESPONSE::{encoded}')

if __name__ == "__main__":
    main()
