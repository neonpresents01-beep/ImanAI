# ImanAILite/nlp_models.py
"""
مدل‌های پیشرفته پردازش زبان طبیعی
شامل: تشخیص احساسات، کدنویس پایتون، خلاصه‌ساز
"""

import numpy as np
from .models import NeuralNetwork
from .layers import Dense, LSTM, Dropout, Embedding
from .tokenizer import TextTokenizer, CodeTokenizer


class SentimentAnalyzer:
    """تشخیص احساسات متن (مثبت، منفی، خنثی)"""
    
    def __init__(self, vocab_size=5000, embed_dim=64, max_len=100):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_len = max_len
        self.tokenizer = TextTokenizer(vocab_size, max_len)
        self.model = None
    
    def build_model(self):
        """ساخت مدل LSTM برای تشخیص احساسات"""
        self.model = NeuralNetwork("SentimentAnalyzer")
        self.model.add(Embedding(self.vocab_size, self.embed_dim))
        self.model.add(LSTM(self.embed_dim, 32))
        self.model.add(Dropout(0.3))
        self.model.add(Dense(32, 3, 'softmax'))  # 3 کلاس: مثبت، منفی، خنثی
        self.model.compile('cross_entropy', optimizer='adam')
        return self.model
    
    def train_on_persian(self, texts, labels, epochs=30):
        """آموزش روی متن فارسی"""
        self.tokenizer.build_vocab(texts)
        X = np.array([self.tokenizer.encode(t, self.max_len) for t in texts])
        y = np.array(labels)
        return self.model.fit(X, y, epochs=epochs, validation_split=0.1)
    
    def predict(self, text):
        """پیش‌بینی احساس متن"""
        X = self.tokenizer.encode(text, self.max_len).reshape(1, -1)
        pred = self.model.predict(X)[0]
        sentiments = ['منفی', 'خنثی', 'مثبت']
        return sentiments[np.argmax(pred)], np.max(pred)
    
    def save(self, path):
        self.model.save(path)
    
    def load(self, path):
        self.model = NeuralNetwork().load(path)


class CodeGenerator:
    """تولید کد پایتون از توضیحات فارسی"""
    
    def __init__(self, vocab_size=3000, embed_dim=128, max_len=200):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_len = max_len
        self.tokenizer = CodeTokenizer(vocab_size, max_len)
        self.model = None
    
    def build_model(self):
        """ساخت مدل Transformer برای تولید کد"""
        from .models import ImanTransformer
        self.model = ImanTransformer(
            vocab_size=self.vocab_size,
            embed_dim=self.embed_dim,
            num_heads=4,  # کمتر برای 32-bit
            num_layers=2,  # کمتر برای 32-bit
            ff_dim=256
        )
        return self.model
    
    def train(self, code_samples, descriptions, epochs=50):
        """
        آموزش روی جفت‌های (توضیحات, کد)
        
        Args:
            code_samples: لیست کدهای پایتون
            descriptions: لیست توضیحات مربوطه
        """
        # ساخت دیتاست
        texts = []
        for desc, code in zip(descriptions, code_samples):
            texts.append(f"<DESC>{desc}<CODE>{code}")
        
        self.tokenizer.build_vocab(texts)
        return self.model.train(self.tokenizer, texts, epochs=epochs, batch_size=4)
    
    def generate(self, description, max_new_tokens=100):
        """تولید کد از روی توضیح"""
        prompt = f"<DESC>{description}<CODE>"
        return self.model.generate(self.tokenizer, prompt, max_new_tokens, temperature=0.3)
    
    def save(self, path):
        self.model.save(path)
    
    def load(self, path):
        self.model = ImanTransformer().load(path)


class TextSummarizer:
    """خلاصه‌سازی متن (ساده)"""
    
    def __init__(self, vocab_size=10000, embed_dim=128, max_len=200):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_len = max_len
        self.tokenizer = TextTokenizer(vocab_size, max_len)
        self.model = None
    
    def build_model(self):
        """ساخت مدل Encoder-Decoder برای خلاصه‌سازی"""
        self.model = NeuralNetwork("Summarizer")
        # Encoder
        self.model.add(Embedding(self.vocab_size, self.embed_dim))
        self.model.add(LSTM(self.embed_dim, 64))
        # Decoder (ساده شده)
        self.model.add(Dense(64, self.vocab_size, 'softmax'))
        self.model.compile('cross_entropy', optimizer='adam')
        return self.model
    
    def train(self, texts, summaries, epochs=30):
        """
        آموزش روی جفت‌های (متن اصلی, خلاصه)
        """
        all_texts = texts + summaries
        self.tokenizer.build_vocab(all_texts)
        
        X = np.array([self.tokenizer.encode(t, self.max_len) for t in texts])
        y = np.array([self.tokenizer.encode(s, self.max_len) for s in summaries])
        
        return self.model.fit(X, y, epochs=epochs, validation_split=0.1)
    
    def summarize(self, text, max_summary_len=50):
        """خلاصه‌سازی متن"""
        X = self.tokenizer.encode(text, self.max_len).reshape(1, -1)
        pred = self.model.predict(X)
        return self.tokenizer.decode(np.argmax(pred, axis=-1)[0])[:max_summary_len]