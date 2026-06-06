# ImanAILite/__init__.py
"""
ImanAILite - کتابخانه هوش مصنوعی سبک و ماژولار برای 32-bit و 64-bit
"""

from .core import ImanAILite
from .models import NeuralNetwork, ImanTransformer
from .layers import Dense, Dropout, BatchNorm, Conv2D, MaxPool2D, Flatten, LSTM, Attention, Embedding
from .tokenizer import TextTokenizer, CodeTokenizer
from .optimizers import SGD, Adam, RMSprop, AdamW
from .utils import gradient_clipping, LearningRateScheduler, ModelCheckpoint
from .nlp_models import SentimentAnalyzer, CodeGenerator, TextSummarizer
from .vision import SimpleResNet, DataAugmentation
from .audio import AudioProcessor, AudioClassifier

# ============== اضافه کردن Activations و Losses ==============
try:
    from .activations import Activations, Losses
    ACTIVATIONS_AVAILABLE = True
except ImportError:
    ACTIVATIONS_AVAILABLE = False
    # اگر فایل activations وجود نداشت، یک نسخه ساده تعریف کن
    class Activations:
        @staticmethod
        def relu(x): import numpy as np; return np.maximum(0, x)
        @staticmethod
        def sigmoid(x): import numpy as np; return 1 / (1 + np.exp(-np.clip(x, -30, 30)))
        @staticmethod
        def softmax(x): import numpy as np; x = x - np.max(x, axis=-1, keepdims=True); return np.exp(x) / (np.sum(np.exp(x), axis=-1, keepdims=True) + 1e-7)
        @staticmethod
        def linear(x): return x
    
    class Losses:
        @staticmethod
        def mse(y_pred, y_true): import numpy as np; return np.mean((y_pred - y_true) ** 2)
        @staticmethod
        def cross_entropy(y_pred, y_true): import numpy as np; return -np.mean(y_true * np.log(y_pred + 1e-7))

# ============== ماژول گفتار ==============
try:
    from .speech import ImanSpeech, VoiceRecognizer, TextToSpeech
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    # نسخه ساده اگر speech.py وجود نداشت
    class ImanSpeech:
        def __init__(self, *args, **kwargs): pass
        def add_command(self, *args, **kwargs): return self
        def train_interactive(self, *args, **kwargs): return True
        def listen_once(self, *args, **kwargs): return None, 0.0, None
        def speak(self, text): print(f"[TTS]: {text}")
    
    class VoiceRecognizer: pass
    class TextToSpeech: pass

# اضافه کردن نسخه
try:
    from importlib.metadata import version
    __version__ = version("ImanAILite")
except:
    __version__ = "2.6.0"

__author__ = "ImanAI Team"

# ============== لیست نهایی ==============
__all__ = [
    # کلاس اصلی
    "ImanAILite",
    
    # مدل‌ها
    "NeuralNetwork",
    "ImanTransformer",
    "SimpleResNet",
    
    # لایه‌ها
    "Dense", "Dropout", "BatchNorm", "Conv2D", "MaxPool2D", "Flatten", "LSTM", "Attention", "Embedding",
    
    # توابع فعال‌سازی و هزینه
    "Activations", "Losses",
    
    # NLP
    "SentimentAnalyzer",
    "CodeGenerator", 
    "TextSummarizer",
    
    # توکنایزرها
    "TextTokenizer",
    "CodeTokenizer",
    
    # بهینه‌سازها
    "SGD", "Adam", "RMSprop", "AdamW",
    
    # ابزارهای کمکی
    "gradient_clipping", "LearningRateScheduler", "ModelCheckpoint",
    
    # پردازش تصویر
    "DataAugmentation",
    
    # پردازش صدا
    "AudioProcessor", "AudioClassifier",
    
    # ماژول گفتار
    "ImanSpeech",
    "VoiceRecognizer",
    "TextToSpeech",
]