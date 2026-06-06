# ImanAILite/core.py
"""
هسته اصلی ImanAILite - مدیریت مدل‌ها، توکنایزرها و قابلیت‌های هوش مصنوعی
نسخه 2.6.0 - با پشتیبانی از گفتار (Speech) و قابلیت‌های پیشرفته
"""

import numpy as np
import pickle
import os
import warnings
from typing import Optional, List, Dict, Any, Tuple, Callable
from pathlib import Path

from .models import NeuralNetwork, ImanTransformer
from .tokenizer import TextTokenizer
from .layers import Dense, Dropout, BatchNorm, Conv2D, MaxPool2D, Flatten, LSTM
from .activations import Activations, Losses
from .optimizers import SGD, Adam, RMSprop, AdamW
from .utils import gradient_clipping, LearningRateScheduler, ModelCheckpoint
from .nlp_models import SentimentAnalyzer, CodeGenerator, TextSummarizer
from .vision import SimpleResNet, DataAugmentation
from .audio import AudioProcessor, AudioClassifier

# تلاش برای import ماژول گفتار (اختیاری)
try:
    from .speech import ImanSpeech, VoiceRecognizer, TextToSpeech
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False


class ImanAILite:
    """
    کلاس اصلی کتابخانه ImanAILite
    مدیریت تمام مدل‌ها، توکنایزرها و قابلیت‌های هوش مصنوعی
    
    قابلیت‌ها:
    - ساخت و آموزش شبکه‌های عصبی (Dense, CNN, LSTM, Transformer)
    - پردازش زبان طبیعی (تشخیص احساسات، تولید کد، خلاصه‌سازی)
    - بینایی ماشین (ResNet ساده، تشخیص تصویر)
    - پردازش صدا (MFCC, Spectrogram, تشخیص صدا)
    - گفتار (تشخیص فرامین صوتی آفلاین، تبدیل متن به گفتار) 🆕
    """
    
    VERSION = "2.6.0"
    
    def __init__(self, verbose: bool = True):
        """
        راه‌اندازی ImanAILite
        
        Args:
            verbose: نمایش اطلاعات در کنسول
        """
        self.verbose = verbose
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, TextTokenizer] = {}
        
        # ماژول‌های تخصصی
        self.sentiment_analyzer: Optional[SentimentAnalyzer] = None
        self.code_generator: Optional[CodeGenerator] = None
        self.text_summarizer: Optional[TextSummarizer] = None
        self.speech: Optional[ImanSpeech] = None  # ماژول گفتار 🆕
        self.audio_classifier: Optional[AudioClassifier] = None
        
        # آمار
        self.stats = {
            "models_created": 0,
            "models_trained": 0,
            "tokenizers_created": 0,
            "start_time": None
        }
        
        if self.verbose:
            self._print_banner()
    
    def _print_banner(self):
        """نمایش بنر خوش‌آمدگویی"""
        print("=" * 70)
        print(f"🧠 ImanAILite v{self.VERSION} - Complete AI Library for 32-bit")
        print("   Capabilities:")
        print("   📊 Regression & Classification | CNN | LSTM | Transformer")
        print("   📝 NLP: Sentiment | Code Gen | Summarization")
        print("   🖼️ Vision: ResNet | Data Augmentation")
        print("   🎤 Audio: MFCC | Spectrogram | Speech Recognition")
        print("   🗣️ Text-to-Speech (Offline)")  # جدید
        print("   Optimizers: SGD | Adam | RMSprop | AdamW")
        print("   Pure NumPy, Minimal Dependencies")
        print("=" * 70)
    
    # ============== مدل‌های پایه ==============
    
    def create_model(self, name: str) -> NeuralNetwork:
        """
        ایجاد یک مدل خالی شبکه عصبی
        
        Args:
            name: نام مدل (یکتا)
        
        Returns:
            NeuralNetwork: مدل ساخته شده
        """
        if name in self.models:
            warnings.warn(f"مدل '{name}' قبلاً وجود دارد. بازنویسی می‌شود.")
        
        model = NeuralNetwork(name)
        self.models[name] = model
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ مدل '{name}' ایجاد شد")
        
        return model
    
    def get_model(self, name: str) -> Optional[Any]:
        """
        دریافت مدل با نام
        
        Args:
            name: نام مدل
        
        Returns:
            مدل مورد نظر یا None
        """
        return self.models.get(name)
    
    def create_classifier(self, name: str, input_dim: int, num_classes: int,
                         hidden_layers: List[int] = [128, 64],
                         optimizer: str = 'adam', lr: float = 0.001,
                         dropout_rate: float = 0.3) -> NeuralNetwork:
        """
        ایجاد مدل دسته‌بندی (Classification)
        
        Args:
            name: نام مدل
            input_dim: ابعاد ورودی
            num_classes: تعداد کلاس‌ها
            hidden_layers: لیست نورون‌های لایه‌های مخفی
            optimizer: نوع بهینه‌ساز ('sgd', 'adam', 'rmsprop', 'adamw')
            lr: نرخ یادگیری
            dropout_rate: نرخ Dropout (0 = غیرفعال)
        
        Returns:
            NeuralNetwork: مدل ساخته شده
        """
        model = NeuralNetwork(name)
        prev = input_dim
        
        for i, h in enumerate(hidden_layers):
            model.add(Dense(prev, h, 'relu'))
            model.add(BatchNorm(h))
            if dropout_rate > 0:
                model.add(Dropout(dropout_rate))
            prev = h
        
        # لایه خروجی
        if num_classes == 2:
            model.add(Dense(prev, 1, 'sigmoid'))
        else:
            model.add(Dense(prev, num_classes, 'softmax'))
        
        loss = 'binary_cross_entropy' if num_classes == 2 else 'cross_entropy'
        model.compile(loss, optimizer=optimizer, lr=lr)
        
        self.models[name] = model
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ Classifier '{name}': {input_dim} → {hidden_layers} → {num_classes}")
            print(f"   Optimizer: {optimizer} | LR: {lr} | Dropout: {dropout_rate}")
        
        return model
    
    def create_regressor(self, name: str, input_dim: int,
                        hidden_layers: List[int] = [128, 64, 32],
                        optimizer: str = 'adam', lr: float = 0.001,
                        dropout_rate: float = 0.2) -> NeuralNetwork:
        """
        ایجاد مدل رگرسیون (پیش‌بینی عدد)
        
        Args:
            name: نام مدل
            input_dim: ابعاد ورودی
            hidden_layers: لیست نورون‌های لایه‌های مخفی
            optimizer: نوع بهینه‌ساز
            lr: نرخ یادگیری
            dropout_rate: نرخ Dropout
        
        Returns:
            NeuralNetwork: مدل ساخته شده
        """
        model = NeuralNetwork(name)
        prev = input_dim
        
        for h in hidden_layers:
            model.add(Dense(prev, h, 'relu'))
            model.add(BatchNorm(h))
            if dropout_rate > 0:
                model.add(Dropout(dropout_rate))
            prev = h
        
        model.add(Dense(prev, 1, 'linear'))
        model.compile('mse', optimizer=optimizer, lr=lr)
        
        self.models[name] = model
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ Regressor '{name}': {input_dim} → {hidden_layers} → 1")
            print(f"   Optimizer: {optimizer} | LR: {lr}")
        
        return model
    
    def create_cnn(self, name: str, input_shape: Tuple[int, int, int],
                  num_classes: int, optimizer: str = 'adam',
                  lr: float = 0.001) -> NeuralNetwork:
        """
        ایجاد مدل CNN برای تصاویر
        
        Args:
            name: نام مدل
            input_shape: شکل ورودی (height, width, channels)
            num_classes: تعداد کلاس‌ها
            optimizer: نوع بهینه‌ساز
            lr: نرخ یادگیری
        
        Returns:
            NeuralNetwork: مدل ساخته شده
        """
        h, w, c = input_shape
        
        model = NeuralNetwork(name)
        model.add(Conv2D(c, 32, 3, padding=1, activation='relu'))
        model.add(MaxPool2D(2))
        model.add(Conv2D(32, 64, 3, padding=1, activation='relu'))
        model.add(MaxPool2D(2))
        model.add(Flatten())
        
        # محاسبه خودکار ابعاد بعد از flatten
        flat_h, flat_w = h // 4, w // 4
        flat_size = 64 * flat_h * flat_w
        
        model.add(Dense(flat_size, 128, 'relu'))
        model.add(Dropout(0.5))
        model.add(Dense(128, num_classes, 'softmax'))
        model.compile('cross_entropy', optimizer=optimizer, lr=lr)
        
        self.models[name] = model
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ CNN '{name}': {input_shape} → {num_classes} classes")
        
        return model
    
    def create_lstm(self, name: str, input_dim: int, seq_len: int,
                   hidden_dim: int = 64, num_layers: int = 1,
                   optimizer: str = 'adam', lr: float = 0.001) -> NeuralNetwork:
        """
        ایجاد مدل LSTM برای سری‌های زمانی / متن
        
        Args:
            name: نام مدل
            input_dim: ابعاد ورودی در هر گام زمانی
            seq_len: طول دنباله
            hidden_dim: ابعاد لایه پنهان LSTM
            num_layers: تعداد لایه‌های LSTM
            optimizer: نوع بهینه‌ساز
            lr: نرخ یادگیری
        
        Returns:
            NeuralNetwork: مدل ساخته شده
        """
        model = NeuralNetwork(name)
        model.add(LSTM(input_dim, hidden_dim, num_layers))
        model.add(Flatten())
        model.add(Dense(hidden_dim * seq_len, 32, 'relu'))
        model.add(Dense(32, 1, 'linear'))  # رگرسیون
        model.compile('mse', optimizer=optimizer, lr=lr)
        
        self.models[name] = model
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ LSTM '{name}': seq_len={seq_len}, hidden={hidden_dim}, layers={num_layers}")
        
        return model
    
    def create_transformer(self, name: str, vocab_size: int = 10000,
                          embed_dim: int = 128, num_heads: int = 4,
                          num_layers: int = 2, ff_dim: int = 256,
                          optimizer: str = 'adam', lr: float = 0.001) -> ImanTransformer:
        """
        ایجاد مدل Transformer (سبک برای 32-bit)
        
        Args:
            name: نام مدل
            vocab_size: سایز دیکشنری
            embed_dim: ابعاد embedding
            num_heads: تعداد سرهای attention (کمتر برای 32-bit)
            num_layers: تعداد لایه‌ها (کمتر برای 32-bit)
            ff_dim: ابعاد لایه feed-forward
            optimizer: نوع بهینه‌ساز
            lr: نرخ یادگیری
        
        Returns:
            ImanTransformer: مدل ساخته شده
        """
        transformer = ImanTransformer(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_layers=num_layers,
            ff_dim=ff_dim
        )
        transformer.optimizer_name = optimizer
        transformer.learning_rate = lr
        
        self.models[name] = transformer
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ Transformer '{name}': vocab={vocab_size}, embed={embed_dim}")
            print(f"   Layers: {num_layers}, Heads: {num_heads} (optimized for 32-bit)")
        
        return transformer
    
    # ============== توکن‌ساز ==============
    
    def create_tokenizer(self, name: str, vocab_size: int = 10000,
                        max_len: int = 100) -> TextTokenizer:
        """
        ایجاد توکن‌ساز متن (پشتیبانی از فارسی و انگلیسی)
        
        Args:
            name: نام توکن‌ساز
            vocab_size: حداکثر سایز دیکشنری
            max_len: حداکثر طول دنباله
        
        Returns:
            TextTokenizer: توکن‌ساز ساخته شده
        """
        tokenizer = TextTokenizer(vocab_size=vocab_size, max_len=max_len)
        self.tokenizers[name] = tokenizer
        self.stats["tokenizers_created"] += 1
        
        if self.verbose:
            print(f"✅ Tokenizer '{name}': vocab_size={vocab_size}, max_len={max_len}")
        
        return tokenizer
    
    def build_tokenizer(self, name: str, texts: List[str]) -> TextTokenizer:
        """
        ساخت دیکشنری توکن‌ساز از روی متون
        
        Args:
            name: نام توکن‌ساز
            texts: لیست متون برای آموزش توکن‌ساز
        
        Returns:
            TextTokenizer: توکن‌ساز ساخته شده
        """
        if name not in self.tokenizers:
            raise ValueError(f"Tokenizer '{name}' not found. Create it first with create_tokenizer()")
        
        self.tokenizers[name].build_vocab(texts)
        
        if self.verbose:
            vocab_size = self.tokenizers[name].get_vocab_size()
            print(f"✅ Tokenizer '{name}' built: {vocab_size} unique tokens")
        
        return self.tokenizers[name]
    
    def encode_text(self, tokenizer_name: str, text: str) -> np.ndarray:
        """تبدیل متن به توکن‌ها"""
        if tokenizer_name not in self.tokenizers:
            raise ValueError(f"Tokenizer '{tokenizer_name}' not found")
        return self.tokenizers[tokenizer_name].encode(text)
    
    def decode_text(self, tokenizer_name: str, tokens: np.ndarray) -> str:
        """تبدیل توکن‌ها به متن"""
        if tokenizer_name not in self.tokenizers:
            raise ValueError(f"Tokenizer '{tokenizer_name}' not found")
        return self.tokenizers[tokenizer_name].decode(tokens)
    
    # ============== آموزش و پیش‌بینی ==============
    
    def train(self, name: str, X: np.ndarray, y: np.ndarray,
             epochs: int = 100, batch_size: int = 32, lr: float = 0.001,
             validation_split: float = 0.1, use_lr_scheduler: bool = False,
             verbose: bool = True) -> List[float]:
        """
        آموزش مدل
        
        Args:
            name: نام مدل
            X: داده‌های ورودی
            y: برچسب‌ها
            epochs: تعداد دوره‌های آموزش
            batch_size: اندازه بچ
            lr: نرخ یادگیری
            validation_split: نسبت داده‌های اعتبارسنجی
            use_lr_scheduler: فعال کردن کاهش نرخ یادگیری
            verbose: نمایش جزئیات
        
        Returns:
            List[float]: تاریخچه خطا
        """
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found")
        
        model = self.models[name]
        
        # فعال کردن LR scheduler اگر درخواست شده
        if use_lr_scheduler and hasattr(model, 'set_lr_scheduler'):
            model.set_lr_scheduler(strategy='step', step_size=30, gamma=0.5)
        
        loss_history = model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            validation_split=validation_split,
            verbose=verbose
        )
        
        self.stats["models_trained"] += 1
        
        return loss_history
    
    def predict(self, name: str, X: np.ndarray) -> np.ndarray:
        """
        پیش‌بینی با مدل
        
        Args:
            name: نام مدل
            X: داده‌های ورودی
        
        Returns:
            np.ndarray: خروجی پیش‌بینی شده
        """
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found")
        
        return self.models[name].predict(X)
    
    def evaluate(self, name: str, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        ارزیابی مدل روی داده‌های تست
        
        Args:
            name: نام مدل
            X: داده‌های ورودی
            y: برچسب‌های واقعی
        
        Returns:
            Dict: معیارهای ارزیابی
        """
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found")
        
        model = self.models[name]
        y_pred = model.predict(X)
        
        results = {}
        
        # محاسبه دقت برای دسته‌بندی
        if len(y_pred.shape) > 1 and y_pred.shape[1] > 1:
            y_pred_class = np.argmax(y_pred, axis=1)
            y_true_class = np.argmax(y, axis=1) if len(y.shape) > 1 else y
            accuracy = np.mean(y_pred_class == y_true_class)
            results['accuracy'] = float(accuracy)
        elif len(y_pred.shape) > 1 and y_pred.shape[1] == 1:
            y_pred_binary = (y_pred > 0.5).astype(int)
            y_true_binary = y
            accuracy = np.mean(y_pred_binary.flatten() == y_true_binary.flatten())
            results['accuracy'] = float(accuracy)
        else:
            # رگرسیون
            mse = np.mean((y_pred.flatten() - y.flatten()) ** 2)
            mae = np.mean(np.abs(y_pred.flatten() - y.flatten()))
            results['mse'] = float(mse)
            results['mae'] = float(mae)
        
        if self.verbose:
            print(f"📊 Evaluation '{name}': {results}")
        
        return results
    
    def summary(self, name: str):
        """نمایش خلاصه مدل"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found")
        self.models[name].summary()
    
    # ============== Transformer ==============
    
    def train_transformer(self, name: str, texts: List[str],
                         tokenizer_name: Optional[str] = None,
                         epochs: int = 50, batch_size: int = 8,
                         lr: float = 0.001) -> List[float]:
        """
        آموزش Transformer روی متن‌ها
        
        Args:
            name: نام مدل Transformer
            texts: لیست متن‌ها برای آموزش
            tokenizer_name: نام توکن‌ساز (اگر None باشد، جدید ساخته می‌شود)
            epochs: تعداد دوره‌ها
            batch_size: اندازه بچ
            lr: نرخ یادگیری
        
        Returns:
            List[float]: تاریخچه خطا
        """
        if name not in self.models:
            raise ValueError(f"Transformer '{name}' not found")
        
        transformer = self.models[name]
        
        # دریافت یا ساخت توکن‌ساز
        if tokenizer_name and tokenizer_name in self.tokenizers:
            tokenizer = self.tokenizers[tokenizer_name]
        else:
            tokenizer = TextTokenizer(vocab_size=transformer.vocab_size, max_len=transformer.max_len)
            tokenizer.build_vocab(texts)
            tok_name = tokenizer_name or f"{name}_tok"
            self.tokenizers[tok_name] = tokenizer
            tokenizer = self.tokenizers[tok_name]
        
        return transformer.train(tokenizer, texts, epochs, batch_size, lr)
    
    def generate_text(self, name: str, start_text: str,
                     tokenizer_name: Optional[str] = None,
                     max_new_tokens: int = 50,
                     temperature: float = 0.8) -> str:
        """
        تولید متن با Transformer
        
        Args:
            name: نام مدل Transformer
            start_text: متن شروع
            tokenizer_name: نام توکن‌ساز
            max_new_tokens: حداکثر توکن‌های جدید
            temperature: دمای sampling (بالاتر = خلاقیت بیشتر)
        
        Returns:
            str: متن تولید شده
        """
        if name not in self.models:
            raise ValueError(f"Transformer '{name}' not found")
        
        transformer = self.models[name]
        
        # پیدا کردن توکن‌ساز مناسب
        tokenizer = None
        if tokenizer_name and tokenizer_name in self.tokenizers:
            tokenizer = self.tokenizers[tokenizer_name]
        elif f"{name}_tok" in self.tokenizers:
            tokenizer = self.tokenizers[f"{name}_tok"]
        
        if tokenizer is None:
            raise ValueError(f"Tokenizer not found for '{name}'. Please create one first.")
        
        return transformer.generate(tokenizer, start_text, max_new_tokens, temperature)
    
    # ============== NLP Models ==============
    
    def create_sentiment_analyzer(self, vocab_size: int = 5000,
                                  embed_dim: int = 64,
                                  max_len: int = 100) -> SentimentAnalyzer:
        """ایجاد مدل تشخیص احساسات"""
        self.sentiment_analyzer = SentimentAnalyzer(vocab_size, embed_dim, max_len)
        self.sentiment_analyzer.build_model()
        
        if self.verbose:
            print("✅ Sentiment Analyzer created")
        
        return self.sentiment_analyzer
    
    def create_code_generator(self, vocab_size: int = 3000,
                             embed_dim: int = 128,
                             max_len: int = 200) -> CodeGenerator:
        """ایجاد مدل تولید کد پایتون"""
        self.code_generator = CodeGenerator(vocab_size, embed_dim, max_len)
        self.code_generator.build_model()
        
        if self.verbose:
            print("✅ Code Generator created")
        
        return self.code_generator
    
    def create_summarizer(self, vocab_size: int = 10000,
                         embed_dim: int = 128,
                         max_len: int = 200) -> TextSummarizer:
        """ایجاد مدل خلاصه‌سازی متن"""
        self.text_summarizer = TextSummarizer(vocab_size, embed_dim, max_len)
        self.text_summarizer.build_model()
        
        if self.verbose:
            print("✅ Text Summarizer created")
        
        return self.text_summarizer
    
    # ============== Speech (NEW!) ==============
    
    def init_speech(self, model_path: Optional[str] = None) -> 'ImanAILite':
        """
        راه‌اندازی ماژول گفتار (تشخیص صدا و TTS آفلاین)
        
        Args:
            model_path: مسیر ذخیره مدل‌های صوتی
        
        Returns:
            self (برای زنجیره‌ای کردن)
        
        Example:
            >>> ai = ImanAILite()
            >>> ai.init_speech()
            >>> ai.add_voice_command("hello", ["سلام", "درود"])
            >>> ai.train_voice_command("hello")
            >>> result = ai.listen()
        """
        if not SPEECH_AVAILABLE:
            raise ImportError("ماژول گفتار در دسترس نیست. مطمئن شوید 'speech.py' در کنار فایل‌های دیگر است.")
        
        self.speech = ImanSpeech(model_path)
        return self
    
    def add_voice_command(self, key: str, phrases: List[str],
                         category: str = "general",
                         handler: Optional[Callable] = None) -> 'ImanAILite':
        """
        اضافه کردن فرمان صوتی جدید
        
        Args:
            key: شناسه یکتای فرمان
            phrases: لیست عبارات معادل (حداقل یکی)
            category: دسته‌بندی (financial, reporting, system, ...)
            handler: تابعی که با تشخیص فرمان اجرا می‌شود
        
        Returns:
            self (برای زنجیره‌ای کردن)
        """
        if not self.speech:
            self.init_speech()
        
        self.speech.add_command(key, phrases, category, handler)
        return self
    
    def train_voice_command(self, command_key: str, samples_count: int = 5) -> bool:
        """
        آموزش تعاملی یک فرمان صوتی
        
        Args:
            command_key: کلید فرمان (که با add_voice_command تعریف شده)
            samples_count: تعداد نمونه‌های مورد نیاز (پیشنهاد: 5)
        
        Returns:
            bool: موفقیت آموزش
        
        Example:
            >>> ai.add_voice_command("cash", ["موجودی صندوق", "صندوق چقدره"])
            >>> ai.train_voice_command("cash")  # 5 بار عبارت را بگویید
        """
        if not self.speech:
            self.init_speech()
        
        if self.verbose:
            print(f"\n🎤 Training voice command: '{command_key}'")
        
        return self.speech.train_interactive(command_key, samples_count)
    
    def listen(self, duration: float = 2.0, timeout: float = 3.0) -> Tuple[Optional[str], float, Optional[str]]:
        """
        گوش دادن به یک فرمان صوتی
        
        Args:
            duration: مدت زمان ضبط پس از تشخیص صدا (ثانیه)
            timeout: حداکثر زمان انتظار برای شروع صحبت (ثانیه)
        
        Returns:
            Tuple: (command_key, confidence, detected_phrase)
        
        Example:
            >>> command, confidence, phrase = ai.listen()
            >>> if command:
            ...     print(f"Detected: {phrase} ({confidence:.0%})")
        """
        if not self.speech:
            self.init_speech()
        
        return self.speech.listen_once(duration, timeout)
    
    def speak(self, text: str, async_mode: bool = True):
        """
        تبدیل متن به گفتار (Text-to-Speech)
        
        Args:
            text: متن فارسی برای گفتن
            async_mode: اجرای غیرهمزمان (پیش‌فرض True)
        
        Example:
            >>> ai.speak("سلام! چطور می‌توانم کمک کنم؟")
        """
        if not self.speech:
            self.init_speech()
        
        self.speech.speak(text, async_mode)
    
    def set_voice(self, rate: Optional[int] = None, volume: Optional[float] = None):
        """
        تنظیمات صدای TTS
        
        Args:
            rate: سرعت گفتار (مثلاً 100 تا 200)
            volume: حجم صدا (0.0 تا 1.0)
        """
        if not self.speech:
            self.init_speech()
        
        self.speech.set_voice(rate, volume)
    
    def get_speech_stats(self) -> dict:
        """دریافت آمار ماژول گفتار"""
        if not self.speech:
            return {"speech_initialized": False}
        return self.speech.get_stats()
    
    # ============== Audio Processing ==============
    
    def create_audio_classifier(self, num_classes: int,
                               input_length: int = 100,
                               n_mfcc: int = 13,
                               model_type: str = 'cnn') -> AudioClassifier:
        """
        ایجاد مدل دسته‌بندی صدا
        
        Args:
            num_classes: تعداد کلاس‌ها
            input_length: طول ورودی
            n_mfcc: تعداد ضرایب MFCC
            model_type: نوع مدل ('cnn' یا 'rnn')
        
        Returns:
            AudioClassifier: مدل ساخته شده
        """
        self.audio_classifier = AudioClassifier(num_classes, input_length, n_mfcc)
        
        if model_type == 'cnn':
            self.audio_classifier.build_cnn_model()
        else:
            self.audio_classifier.build_rnn_model()
        
        if self.verbose:
            print(f"✅ Audio Classifier created: {model_type.upper()} model, {num_classes} classes")
        
        return self.audio_classifier
    
    def extract_mfcc(self, audio_file: str, n_mfcc: int = 13) -> Optional[np.ndarray]:
        """
        استخراج ویژگی MFCC از فایل صوتی
        
        Args:
            audio_file: مسیر فایل صوتی
            n_mfcc: تعداد ضرایب MFCC
        
        Returns:
            np.ndarray: ویژگی‌های MFCC
        """
        audio, sr = AudioProcessor.load_audio(audio_file)
        if audio is not None:
            return AudioProcessor.mfcc(audio, sr, n_mfcc)
        return None
    
    # ============== Vision ==============
    
    def create_resnet(self, name: str, input_shape: Tuple[int, int, int],
                     num_classes: int, depth: int = 18) -> SimpleResNet:
        """ایجاد مدل ResNet ساده"""
        resnet = SimpleResNet(input_shape, num_classes, depth)
        resnet.build()
        
        self.models[name] = resnet
        self.stats["models_created"] += 1
        
        if self.verbose:
            print(f"✅ ResNet-{depth} '{name}': {input_shape} → {num_classes} classes")
        
        return resnet
    
    def augment_images(self, images: np.ndarray, labels: np.ndarray,
                      augment_prob: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        افزایش داده تصاویر (Data Augmentation)
        
        Args:
            images: آرایه تصاویر
            labels: برچسب‌ها
            augment_prob: احتمال اعمال augmentation
        
        Returns:
            Tuple: (images_augmented, labels_augmented)
        """
        return DataAugmentation.augment_batch(images, labels, augment_prob)
    
    # ============== Model Management ==============
    
    def save(self, name: str, path: str):
        """ذخیره مدل در فایل"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found")
        self.models[name].save(path)
    
    def load(self, name: str, path: str) -> Any:
        """بارگذاری مدل از فایل"""
        if name in self.models and hasattr(self.models[name], 'load'):
            self.models[name].load(path)
        else:
            # تشخیص خودکار نوع مدل
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            if 'num_layers' in data and 'num_heads' in data:
                model = ImanTransformer().load(path)
            else:
                model = NeuralNetwork().load(path)
            
            self.models[name] = model
        
        if self.verbose:
            print(f"📂 Model '{name}' loaded from {path}")
        
        return self.models[name]
    
    def delete_model(self, name: str):
        """حذف مدل"""
        if name in self.models:
            del self.models[name]
            if self.verbose:
                print(f"🗑️ Model '{name}' deleted")
    
    def list_models(self) -> List[str]:
        """لیست نام همه مدل‌ها"""
        return list(self.models.keys())
    
    def list_tokenizers(self) -> List[str]:
        """لیست نام همه توکن‌سازها"""
        return list(self.tokenizers.keys())
    
    def get_model_info(self, name: str) -> Optional[Dict]:
        """دریافت اطلاعات مدل"""
        if name not in self.models:
            return None
        
        model = self.models[name]
        info = {
            'name': name,
            'type': type(model).__name__,
        }
        
        if hasattr(model, 'layers'):
            info['layers'] = len(model.layers)
        if hasattr(model, 'optimizer_name'):
            info['optimizer'] = model.optimizer_name
        if hasattr(model, 'vocab_size'):
            info['vocab_size'] = model.vocab_size
        
        return info
    
    def get_stats(self) -> Dict:
        """دریافت آمار کلی کتابخانه"""
        return {
            **self.stats,
            "models": self.list_models(),
            "tokenizers": self.list_tokenizers(),
            "speech_available": SPEECH_AVAILABLE,
            "speech_initialized": self.speech is not None
        }
    
    def reset(self):
        """بازنشانی کامل کتابخانه"""
        self.models.clear()
        self.tokenizers.clear()
        self.sentiment_analyzer = None
        self.code_generator = None
        self.text_summarizer = None
        self.speech = None
        self.audio_classifier = None
        self.stats = {
            "models_created": 0,
            "models_trained": 0,
            "tokenizers_created": 0,
            "start_time": None
        }
        
        if self.verbose:
            print("🔄 ImanAILite reset completed")