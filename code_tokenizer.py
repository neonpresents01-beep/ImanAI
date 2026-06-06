# ImanAILite/code_tokenizer.py
"""
توکنایزر تخصصی برای کد پایتون
با حفظ فرمت، indent و کلمات کلیدی
"""

import re
from typing import List, Dict, Tuple


class PythonCodeTokenizer:
    """توکنایزر مخصوص کد پایتون"""
    
    def __init__(self, max_vocab=5000):
        self.max_vocab = max_vocab
        
        # کلمات کلیدی پایتون
        self.keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 
            'except', 'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield'
        }
        
        # توابع توکار
        self.builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir', 'enumerate',
            'filter', 'float', 'format', 'frozenset', 'getattr', 'hasattr', 'hash',
            'help', 'hex', 'id', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'map', 'max', 'min', 'next', 'object', 'oct', 'open', 'ord',
            'pow', 'print', 'range', 'repr', 'reversed', 'round', 'set', 'setattr',
            'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip'
        }
        
        # عملگرها
        self.operators = {
            '+', '-', '*', '/', '//', '%', '**', '=', '==', '!=', '<', '>', 
            '<=', '>=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '>>=', '<<=',
            '&', '|', '^', '~', '>>', '<<', '->', ':=', '@'
        }
        
        # جداکننده‌ها
        self.delimiters = {'(', ')', '[', ']', '{', '}', ',', ':', ';', '.', '@'}
        
        # توکن‌های ویژه
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<START>': 2,
            '<END>': 3,
            '<INDENT>': 4,     # افزایش indent
            '<DEDENT>': 5,     # کاهش indent
            '<NEWLINE>': 6,    # خط جدید
        }
        
        self.vocab = self.special_tokens.copy()
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        self.next_id = len(self.special_tokens)
        
        # اضافه کردن کلمات کلیدی به vocab
        for kw in self.keywords:
            self._add_token(f'KW_{kw}')
        
        for blt in self.builtins:
            self._add_token(f'BLT_{blt}')
        
        for op in self.operators:
            self._add_token(f'OP_{op}')
        
        for delim in self.delimiters:
            self._add_token(f'DEL_{delim}')
    
    def _add_token(self, token: str):
        """اضافه کردن توکن جدید به vocab"""
        if token not in self.vocab and len(self.vocab) < self.max_vocab:
            self.vocab[token] = self.next_id
            self.reverse_vocab[self.next_id] = token
            self.next_id += 1
    
    def encode(self, code: str, max_length: int = 500) -> List[int]:
        """تبدیل کد پایتون به لیست توکن‌ها"""
        tokens = [self.vocab['<START>']]
        
        lines = code.strip().split('\n')
        indent_level = 0
        
        for line in lines:
            # محاسبه indent سطح فعلی
            stripped = line.lstrip()
            spaces = len(line) - len(stripped)
            current_indent = spaces // 4
            
            # اضافه کردن توکن‌های INDENT/DEDENT
            while current_indent > indent_level:
                tokens.append(self.vocab['<INDENT>'])
                indent_level += 1
            while current_indent < indent_level:
                tokens.append(self.vocab['<DEDENT>'])
                indent_level -= 1
            
            # توکنایزر کلمات خط
            line_tokens = self._tokenize_line(stripped)
            tokens.extend(line_tokens)
            tokens.append(self.vocab['<NEWLINE>'])
        
        # بستن indentهای باز
        while indent_level > 0:
            tokens.append(self.vocab['<DEDENT>'])
            indent_level -= 1
        
        tokens.append(self.vocab['<END>'])
        
        # محدود کردن طول
        if len(tokens) > max_length:
            tokens = tokens[:max_length-1] + [self.vocab['<END>']]
        
        return tokens
    
    def _tokenize_line(self, line: str) -> List[int]:
        """توکنایزر یک خط کد"""
        tokens = []
        i = 0
        length = len(line)
        
        while i < length:
            # کامنت
            if line[i] == '#':
                # کامنت رو نادیده می‌گیریم
                break
            
            # رشته (string)
            if line[i] in ('"', "'"):
                quote = line[i]
                j = i + 1
                while j < length and line[j] != quote:
                    if line[j] == '\\':  # escape
                        j += 1
                    j += 1
                string_literal = line[i:j+1]
                self._add_token(f'STR_{string_literal[:20]}')  # فقط ۲۰ کاراکتر اول
                tokens.append(self.vocab.get(f'STR_{string_literal[:20]}', self.vocab['<UNK>']))
                i = j + 1
                continue
            
            # عدد
            if line[i].isdigit():
                j = i
                while j < length and (line[j].isdigit() or line[j] == '.'):
                    j += 1
                num = line[i:j]
                self._add_token(f'NUM_{num}')
                tokens.append(self.vocab.get(f'NUM_{num}', self.vocab['<UNK>']))
                i = j
                continue
            
            # کلمه (identifier)
            if line[i].isalpha() or line[i] == '_':
                j = i
                while j < length and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]
                
                # تشخیص کلمه کلیدی
                if word in self.keywords:
                    tokens.append(self.vocab[f'KW_{word}'])
                elif word in self.builtins:
                    tokens.append(self.vocab[f'BLT_{word}'])
                else:
                    # شناسه (متغیر یا تابع)
                    self._add_token(f'ID_{word[:50]}')
                    tokens.append(self.vocab.get(f'ID_{word[:50]}', self.vocab['<UNK>']))
                
                i = j
                continue
            
            # عملگرها و جداکننده‌ها
            # عملگر دو کاراکتری
            if i + 1 < length and line[i:i+2] in self.operators:
                self._add_token(f'OP_{line[i:i+2]}')
                tokens.append(self.vocab[f'OP_{line[i:i+2]}'])
                i += 2
                continue
            
            # عملگر یا جداکننده یک کاراکتری
            if line[i] in self.operators:
                self._add_token(f'OP_{line[i]}')
                tokens.append(self.vocab[f'OP_{line[i]}'])
                i += 1
                continue
            
            if line[i] in self.delimiters:
                self._add_token(f'DEL_{line[i]}')
                tokens.append(self.vocab[f'DEL_{line[i]}'])
                i += 1
                continue
            
            # فاصله (نادیده گرفته می‌شود)
            if line[i].isspace():
                i += 1
                continue
            
            # کاراکتر ناشناخته
            tokens.append(self.vocab['<UNK>'])
            i += 1
        
        return tokens
    
    def decode(self, tokens: List[int]) -> str:
        """تبدیل لیست توکن‌ها به کد پایتون"""
        code_lines = []
        current_line = []
        indent_level = 0
        
        for token_id in tokens:
            if token_id == self.vocab['<START>']:
                continue
            
            if token_id == self.vocab['<END>']:
                break
            
            if token_id == self.vocab['<NEWLINE>']:
                if current_line:
                    code_lines.append('    ' * indent_level + ''.join(current_line))
                    current_line = []
                continue
            
            if token_id == self.vocab['<INDENT>']:
                indent_level += 1
                continue
            
            if token_id == self.vocab['<DEDENT>']:
                indent_level = max(0, indent_level - 1)
                continue
            
            token = self.reverse_vocab.get(token_id, '<UNK>')
            
            # حذف پیشوندها
            if token.startswith('KW_'):
                current_line.append(token[3:])
            elif token.startswith('BLT_'):
                current_line.append(token[4:])
            elif token.startswith('OP_'):
                current_line.append(token[3:])
            elif token.startswith('DEL_'):
                current_line.append(token[4:])
            elif token.startswith('ID_'):
                current_line.append(token[3:])
            elif token.startswith('NUM_'):
                current_line.append(token[4:])
            elif token.startswith('STR_'):
                current_line.append(token[4:])
            else:
                current_line.append(token)
        
        # آخرین خط
        if current_line:
            code_lines.append('    ' * indent_level + ''.join(current_line))
        
        return '\n'.join(code_lines)
    
    def get_vocab_size(self) -> int:
        return len(self.vocab)
    
    def save(self, path: str):
        """ذخیره توکنایزر"""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'vocab': self.vocab,
                'reverse_vocab': self.reverse_vocab,
                'next_id': self.next_id,
                'max_vocab': self.max_vocab
            }, f)
    
    def load(self, path: str):
        """بارگذاری توکنایزر"""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vocab = data['vocab']
            self.reverse_vocab = data['reverse_vocab']
            self.next_id = data['next_id']
            self.max_vocab = data['max_vocab']