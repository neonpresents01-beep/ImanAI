# ImanAILite/tokenizer.py
import numpy as np
import re
from collections import Counter


class TextTokenizer:
    """
    توکن‌ساز پیشرفته با پشتیبانی از:
    - زبان فارسی
    - زبان انگلیسی
    - اعداد
    - علائم نگارشی
    - پشتیبانی از کلمات خاص (OOV)
    """
    
    def __init__(self, vocab_size=10000, max_len=100):
        self.vocab_size = vocab_size
        self.max_len = max_len
        
        # دیکشنری‌ها
        self.word_to_idx = {}
        self.idx_to_word = {}
        
        # آمار
        self.vocab = set()
        self.word_counts = Counter()
        
        # توکن‌های ویژه
        self.special_tokens = {
            '<PAD>': 0,      # padding
            '<UNK>': 1,      # unknown (کلمه ناشناخته)
            '<START>': 2,    # شروع جمله
            '<END>': 3,      # پایان جمله
            '<NUM>': 4,      # عدد
            '<PUNC>': 5,     # علامت نگارشی
            '<URL>': 6,      # آدرس وب
            '<EMAIL>': 7,    # ایمیل
            '<DATE>': 8      # تاریخ
        }
        
        # اضافه کردن توکن‌های ویژه
        for token, idx in self.special_tokens.items():
            self.word_to_idx[token] = idx
            self.idx_to_word[idx] = token
        
        self.next_id = len(self.special_tokens)
        
        # الگوهای regex برای تشخیص تخصصی
        self.patterns = {
            'url': r'https?://[^\s]+|www\.[^\s]+',
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'date': r'\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4}',
            'number': r'\d+(?:\.\d+)?',
            'persian_char': r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
            'english_char': r'[a-zA-Z]',
            'punctuation': r'[!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~،؛؟]'
        }
    
    def _is_persian(self, char):
        """تشخیص کاراکتر فارسی"""
        persian_range = [
            (0x0600, 0x06FF),   # عربی/فارسی
            (0x0750, 0x077F),   # عربی توسعه
            (0x08A0, 0x08FF),   # عربی توسعه
            (0xFB50, 0xFDFF),   # اشکال عربی
            (0xFE70, 0xFEFF),   # اشکال عربی
        ]
        code = ord(char)
        return any(start <= code <= end for start, end in persian_range)
    
    def _preprocess(self, text: str) -> str:
        """پیش‌پردازش متن"""
        # جایگزینی ایمیل
        text = re.sub(self.patterns['email'], ' <EMAIL> ', text)
        
        # جایگزینی URL
        text = re.sub(self.patterns['url'], ' <URL> ', text)
        
        # جایگزینی تاریخ
        text = re.sub(self.patterns['date'], ' <DATE> ', text)
        
        # جایگزینی اعداد با <NUM>
        text = re.sub(self.patterns['number'], ' <NUM> ', text)
        
        # جایگزینی علامت‌های نگارشی خاص فارسی
        persian_punctuation = '،؛؟٪×÷»«'
        for punc in persian_punctuation:
            text = text.replace(punc, f' {punc} ')
        
        # جایگزینی علامت‌های نگارشی انگلیسی
        for punc in '.,!?;:()[]{}"\'':
            text = text.replace(punc, f' {punc} ')
        
        # حذف فاصله‌های اضافی
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _tokenize_line(self, text: str):
        """تقسیم متن به توکن‌های ساده"""
        # پیش‌پردازش
        text = self._preprocess(text)
        
        # تقسیم بر اساس فاصله
        tokens = text.split()
        
        return tokens
    
    def build_vocab(self, texts):
        """
        ساخت دیکشنری واژگان از مجموعه متون
        
        Args:
            texts: لیست متن‌ها (لیست رشته‌ها)
        """
        print("📚 Building vocabulary...")
        
        # توکن‌های ویژه از قبل اضافه شده‌اند
        
        for text in texts:
            tokens = self._tokenize_line(text)
            for token in tokens:
                # اگر توکن ویژه نیست، به دیکشنری اضافه کن
                if not token.startswith('<') and not token.endswith('>'):
                    self.word_counts[token] += 1
                    self.vocab.add(token)
        
        # گرفتن پرتکرارترین کلمات
        common_words = [word for word, _ in self.word_counts.most_common(self.vocab_size - self.next_id)]
        
        # اضافه کردن به دیکشنری
        for word in common_words:
            if word not in self.word_to_idx:
                self.word_to_idx[word] = self.next_id
                self.idx_to_word[self.next_id] = word
                self.next_id += 1
        
        # اضافه کردن توکن <UNK> برای کلمات ناشناخته
        if '<UNK>' not in self.word_to_idx:
            self.word_to_idx['<UNK>'] = self.next_id
            self.idx_to_word[self.next_id] = '<UNK>'
            self.next_id += 1
        
        print(f"✅ Vocab size: {len(self.word_to_idx)} (Special: {len(self.special_tokens)}, Words: {len(self.word_to_idx) - len(self.special_tokens)})")
        
        # آمار زبان
        persian_count = sum(1 for w in self.word_to_idx if self._is_persian(w[0]) if w)
        print(f"📊 Stats: {persian_count} Persian words in vocab")
    
    def encode(self, text: str, max_len=None) -> np.ndarray:
        """
        تبدیل متن به لیست توکن‌ها
        
        Args:
            text: متن ورودی
            max_len: حداکثر طول (اگر None باشه از self.max_len استفاده می‌کنه)
        
        Returns:
            آرایه NumPy از توکن‌ها
        """
        if max_len is None:
            max_len = self.max_len
        
        # توکن‌سازی
        tokens = self._tokenize_line(text)
        
        # اضافه کردن <START> و <END>
        token_ids = [self.word_to_idx.get('<START>')]
        
        for token in tokens:
            # توکن‌های ویژه رو مستقیم استفاده کن
            if token.startswith('<') and token.endswith('>'):
                token_id = self.word_to_idx.get(token, self.word_to_idx.get('<UNK>'))
            else:
                token_id = self.word_to_idx.get(token, self.word_to_idx.get('<UNK>'))
            token_ids.append(token_id)
        
        token_ids.append(self.word_to_idx.get('<END>'))
        
        # Padding یا Truncation
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len-1] + [self.word_to_idx.get('<END>')]
        elif len(token_ids) < max_len:
            token_ids += [self.word_to_idx.get('<PAD>')] * (max_len - len(token_ids))
        
        return np.array(token_ids[:max_len], dtype=np.int32)
    
    def decode(self, tokens, ignore_special=True) -> str:
        """
        تبدیل لیست توکن‌ها به متن
        
        Args:
            tokens: لیست یا آرایه توکن‌ها
            ignore_special: چشم‌پوشی از توکن‌های ویژه (<PAD>, <START>, <END>)
        
        Returns:
            متن بازسازی شده
        """
        # اطمینان از لیست بودن (اگر NumPy array بود)
        if hasattr(tokens, 'tolist'):
            tokens = tokens.tolist()
        
        words = []
        
        for token_id in tokens:
            if token_id not in self.idx_to_word:
                continue
            
            word = self.idx_to_word[token_id]
            
            if ignore_special and word in ['<PAD>', '<START>', '<END>', '<UNK>', '<NUM>', '<PUNC>', '<URL>', '<EMAIL>', '<DATE>']:
                if word == '<NUM>':
                    words.append('[عدد]')
                elif word == '<URL>':
                    words.append('[لینک]')
                elif word == '<EMAIL>':
                    words.append('[ایمیل]')
                elif word == '<DATE>':
                    words.append('[تاریخ]')
                continue
            
            words.append(word)
        
        # بازگرداندن متن
        text = ' '.join(words)
        
        # اصلاح فاصله‌ها با علائم نگارشی فارسی
        for punc in '،؛؟!.':
            text = text.replace(f' {punc}', punc)
        
        return text.strip()
    
    def get_vocab_size(self) -> int:
        """دریافت اندازه دیکشنری"""
        return len(self.word_to_idx)
    
    def get_special_tokens(self) -> dict:
        """دریافت توکن‌های ویژه"""
        return self.special_tokens.copy()
    
    def save(self, path: str):
        """ذخیره توکنایزر در فایل"""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'word_to_idx': self.word_to_idx,
                'idx_to_word': self.idx_to_word,
                'vocab_size': self.vocab_size,
                'max_len': self.max_len,
                'word_counts': self.word_counts,
                'special_tokens': self.special_tokens,
                'next_id': self.next_id
            }, f)
        print(f"💾 Tokenizer saved to {path}")
    
    def load(self, path: str):
        """بارگذاری توکنایزر از فایل"""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.word_to_idx = data['word_to_idx']
            self.idx_to_word = data['idx_to_word']
            self.vocab_size = data['vocab_size']
            self.max_len = data['max_len']
            self.word_counts = data['word_counts']
            self.special_tokens = data['special_tokens']
            self.next_id = data['next_id']
        print(f"📂 Tokenizer loaded from {path}")


class CodeTokenizer(TextTokenizer):
    """توکنایزر مخصوص کد پایتون - از TextTokenizer ارث‌بری می‌کنه"""
    
    def __init__(self, vocab_size=5000, max_len=200):
        super().__init__(vocab_size, max_len)
        
        self.add_python_keywords()
    
    def add_python_keywords(self):
        """اضافه کردن کلمات کلیدی پایتون به دیکشنری"""
        python_keywords = [
            'def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif',
            'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'lambda',
            'yield', 'assert', 'break', 'continue', 'pass', 'raise', 'del',
            'global', 'nonlocal', 'True', 'False', 'None', 'and', 'or', 'not',
            'in', 'is', 'self', 'cls', '__init__', '__str__', '__repr__'
        ]
        
        for keyword in python_keywords:
            if keyword not in self.word_to_idx:
                self.word_to_idx[keyword] = self.next_id
                self.idx_to_word[self.next_id] = keyword
                self.next_id += 1
    
    def _tokenize_line(self, text: str):
        """توکن‌سازی مخصوص کد (حفظ indent و newline)"""
        lines = text.split('\n')
        tokens = []
        
        for line in lines:
            # حفظ ساختار کد
            if line.strip():
                # تقسیم بر اساس فاصله ولی حفظ علامت‌ها
                parts = line.split()
                for part in parts:
                    # توکن‌های خاص کد
                    if part in (':', '=', '==', '!=', '<=', '>=', '+=', '-=', '*=', '/='):
                        tokens.append(part)
                    else:
                        tokens.append(part)
            else:
                tokens.append('<NEWLINE>')
        
        return tokens