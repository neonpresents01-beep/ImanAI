import json
import urllib.parse
import os

class AI:
    def chat(self, msg):
        msg_lower = msg.lower()
        responses = {
            'سلام': '👋 سلام! من ImanAI هستم. چطور میتونم کمکت کنم؟',
            'خوبی': '🙂 ممنون! من همیشه آماده کمکم.',
            'اسمت': '🤖 اسم من ImanAI هست.',
            'موجودی صندوق': '💰 موجودی صندوق: 15,320,000 ریال',
            'موجودی بانک': '🏦 موجودی بانک: 82,450,000 ریال',
            'فروش امروز': '📈 فروش امروز: 3,200,000 ریال',
            'راهنما': 'سوالات: سلام, موجودی صندوق, موجودی بانک, فروش امروز',
            'خداحافظ': '👋 خداحافظ!'
        }
        for key, resp in responses.items():
            if key in msg_lower:
                return resp
        return f'دریافت شد: {msg[:100]}... (راهنما: \"راهنما\")'

ai = AI()
action = os.environ.get('ACTION', '')
message = os.environ.get('MESSAGE', '')

if action == 'chat':
    result = {'response': ai.chat(message)}
elif action == 'status':
    result = {'status': 'online', 'version': '2.6.0'}
else:
    result = {'status': 'idle'}

encoded = urllib.parse.quote(json.dumps(result))
print(f'IMANAI_RESPONSE::{encoded}')
