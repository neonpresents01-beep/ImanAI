import json
import urllib.parse
import os
import hashlib
import uuid
import time

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key():
    return f"imanai_{uuid.uuid4().hex[:16]}"

action = os.environ.get('ACTION', '')
api_key = os.environ.get('API_KEY', '')
name = os.environ.get('USER_NAME', '')
email = os.environ.get('USER_EMAIL', '')
plan = os.environ.get('USER_PLAN', 'free')
message = os.environ.get('USER_MESSAGE', '')

users = load_users()
result = {}

if action == 'register':
    new_key = generate_api_key()
    users[hash_key(new_key)] = {
        'name': name, 'email': email, 'plan': plan,
        'credits': 10000, 'created_at': time.time()
    }
    save_users(users)
    result = {'success': True, 'api_key': new_key, 'credits': 10000, 'plan': plan}

elif action == 'chat':
    if not api_key:
        result = {'success': False, 'error': 'API Key required'}
    else:
        h = hash_key(api_key)
        if h not in users:
            result = {'success': False, 'error': 'Invalid API Key'}
        elif users[h]['credits'] <= 0:
            result = {'success': False, 'error': 'Insufficient credits'}
        else:
            users[h]['credits'] -= 1
            save_users(users)
            result = {'success': True, 'response': f'دریافت شد: {message[:100]}', 'remaining_credits': users[h]['credits']}

elif action == 'balance':
    if not api_key:
        result = {'success': False, 'error': 'API Key required'}
    else:
        h = hash_key(api_key)
        if h not in users:
            result = {'success': False, 'error': 'Invalid API Key'}
        else:
            result = {'success': True, 'credits': users[h]['credits'], 'plan': users[h]['plan']}

else:
    result = {'error': f'Unknown: {action}'}

print(f'API_RESPONSE::{urllib.parse.quote(json.dumps(result))}')
