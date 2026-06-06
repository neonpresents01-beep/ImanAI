# ImanAILite/speech.py
"""
ماژول گفتار ImanAI - تبدیل گفتار به متن و متن به گفتار آفلاین
نسخه 1.0 - مناسب برای 32-bit و 64-bit
"""

import numpy as np
import threading
import pickle
import os
import time
import struct
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict

from .audio import AudioProcessor

# تلاش برای import کتابخانه‌های صوتی
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


@dataclass
class VoiceCommand:
    """مدل فرمان صوتی"""
    key: str
    phrases: List[str]
    category: str = "general"
    handler: Optional[Callable] = None
    acoustic_model: Optional[np.ndarray] = None
    threshold: float = 0.65
    usage_count: int = 0
    is_trained: bool = False


class VoiceRecognizer:
    """
    موتور تشخیص فرامین صوتی آفلاین
    استخراج ویژگی و تشخیص با روش DTW (Dynamic Time Warping)
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frame_length = 400  # 25ms
        self.commands: Dict[str, VoiceCommand] = {}
        self.noise_profile = None
        
    def extract_features(self, audio_data: bytes) -> Optional[np.ndarray]:
        """
        استخراج ویژگی‌های صوتی (MFCC-like)
        
        Args:
            audio_data: داده صوتی خام (bytes)
        
        Returns:
            آرایه ویژگی‌ها یا None
        """
        # تبدیل به numpy array
        samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        
        if len(samples) < self.frame_length:
            return None
        
        # نرمال‌سازی
        samples = samples / 32768.0
        
        # 1. انرژی RMS
        energy = np.sqrt(np.mean(samples**2))
        
        # 2. فرکانس پایه (Pitch)
        f0 = self._estimate_pitch(samples)
        
        # 3. ویژگی‌های طیفی
        spectral = self._spectral_features(samples)
        
        # 4. ضرایب خودهمبستگی
        autocorr = self._autocorrelation_features(samples)
        
        # ترکیب ویژگی‌ها
        features = np.concatenate([
            [energy, f0],
            spectral[:8],
            autocorr[:8]
        ])
        
        # نرمال‌سازی نهایی
        if np.std(features) > 0:
            features = (features - np.mean(features)) / np.std(features)
        
        return features
    
    def _estimate_pitch(self, samples: np.ndarray) -> float:
        """تخمین فرکانس پایه با روش خودهمبستگی"""
        n = len(samples)
        if n < 100:
            return 0
        
        # خودهمبستگی ساده
        corr = np.zeros(n)
        for i in range(n):
            corr[i] = np.sum(samples[:n-i] * samples[i:]) / (n-i)
        
        # محدوده فرکانس گفتار (80-300 Hz)
        min_period = int(self.sample_rate / 300)
        max_period = int(self.sample_rate / 80)
        
        if max_period > len(corr):
            return 0
        
        search_range = corr[min_period:max_period]
        if len(search_range) > 0 and np.max(search_range) > 0:
            max_index = np.argmax(search_range)
            period = min_period + max_index
            if period > 0:
                return self.sample_rate / period
        return 0
    
    def _spectral_features(self, samples: np.ndarray) -> np.ndarray:
        """استخراج ویژگی‌های طیفی با FFT"""
        fft = np.abs(np.fft.rfft(samples))
        
        # تقسیم به 8 باند فرکانسی
        bands = np.array_split(fft, 8)
        features = [np.mean(band) for band in bands]
        
        features = np.array(features)
        if np.sum(features) > 0:
            features = features / np.sum(features)
        
        return features
    
    def _autocorrelation_features(self, samples: np.ndarray) -> np.ndarray:
        """استخراج ضرایب خودهمبستگی"""
        n = len(samples)
        lags = [int(n * i / 10) for i in range(1, 11)]
        
        features = []
        for lag in lags:
            if lag < n:
                corr = np.corrcoef(samples[:-lag], samples[lag:])[0, 1]
                features.append(corr if not np.isnan(corr) else 0)
            else:
                features.append(0)
        
        return np.array(features)
    
    def _calculate_similarity(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """محاسبه شباهت بین دو ویژگی"""
        correlation = np.corrcoef(feat1, feat2)[0, 1]
        return (correlation + 1) / 2
    
    def add_command(self, key: str, phrases: List[str], category: str = "general",
                    handler: Optional[Callable] = None) -> 'VoiceRecognizer':
        """اضافه کردن فرمان جدید"""
        self.commands[key] = VoiceCommand(
            key=key,
            phrases=phrases,
            category=category,
            handler=handler
        )
        return self
    
    def train(self, command_key: str, audio_samples: List[bytes]) -> bool:
        """
        آموزش یک فرمان با نمونه‌های صوتی
        
        Args:
            command_key: کلید فرمان
            audio_samples: لیست داده‌های صوتی (حداقل 3 نمونه)
        
        Returns:
            موفقیت آموزش
        """
        if command_key not in self.commands:
            return False
        
        if len(audio_samples) < 3:
            return False
        
        features_list = []
        for audio in audio_samples:
            feat = self.extract_features(audio)
            if feat is not None:
                features_list.append(feat)
        
        if len(features_list) < 2:
            return False
        
        # میانگین ویژگی‌ها = مدل آکوستیک
        acoustic_model = np.mean(features_list, axis=0)
        
        # محاسبه آستانه تشخیص
        variances = np.var(features_list, axis=0)
        avg_variance = np.mean(variances)
        threshold = max(0.55, 1 - avg_variance * 3)
        
        self.commands[command_key].acoustic_model = acoustic_model
        self.commands[command_key].threshold = threshold
        self.commands[command_key].is_trained = True
        
        return True
    
    def recognize(self, audio_data: bytes) -> Tuple[Optional[str], float, Optional[str]]:
        """
        تشخیص فرمان از روی داده صوتی
        
        Returns:
            (command_key, confidence, detected_phrase)
        """
        features = self.extract_features(audio_data)
        if features is None:
            return None, 0.0, None
        
        best_key = None
        best_score = 0.0
        best_phrase = None
        
        for key, cmd in self.commands.items():
            if cmd.acoustic_model is None:
                continue
            
            similarity = self._calculate_similarity(features, cmd.acoustic_model)
            
            if similarity > best_score and similarity > cmd.threshold:
                best_score = similarity
                best_key = key
                best_phrase = cmd.phrases[0] if cmd.phrases else None
        
        # بروزرسانی آمار
        if best_key:
            self.commands[best_key].usage_count += 1
            
            # اجرای handler
            handler = self.commands[best_key].handler
            if handler and callable(handler):
                threading.Thread(target=handler, args=(best_phrase, best_score)).start()
        
        return best_key, best_score, best_phrase
    
    def record_audio(self, duration: float = 2.0, timeout: float = 3.0) -> Optional[bytes]:
        """ضبط صدا از میکروفون"""
        if not PYAUDIO_AVAILABLE:
            print("⚠️ PyAudio نصب نیست. برای ضبط صدا: pip install pyaudio")
            return None
        
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            start_time = time.time()
            speech_started = False
            
            while (time.time() - start_time) < (timeout + duration):
                data = stream.read(1024, exception_on_overflow=False)
                
                if not speech_started:
                    # بررسی وجود صدا
                    samples = np.frombuffer(data, dtype=np.int16)
                    energy = np.mean(np.abs(samples))
                    if energy > 300:
                        speech_started = True
                        frames.append(data)
                else:
                    frames.append(data)
                    
                    if len(frames) * 1024 / self.sample_rate >= duration:
                        break
            
            stream.stop_stream()
            stream.close()
            
            if frames:
                return b''.join(frames)
            
        except Exception as e:
            print(f"❌ خطا در ضبط: {e}")
        finally:
            audio.terminate()
        
        return None
    
    def get_stats(self) -> dict:
        """دریافت آمار"""
        trained = sum(1 for cmd in self.commands.values() if cmd.is_trained)
        total_usage = sum(cmd.usage_count for cmd in self.commands.values())
        
        return {
            "total_commands": len(self.commands),
            "trained_commands": trained,
            "total_usage": total_usage,
            "categories": list(set(cmd.category for cmd in self.commands.values()))
        }
    
    def save(self, path: str):
        """ذخیره مدل"""
        with open(path, 'wb') as f:
            pickle.dump({
                'commands': self.commands,
                'sample_rate': self.sample_rate,
                'noise_profile': self.noise_profile
            }, f)
    
    def load(self, path: str):
        """بارگذاری مدل"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
            self.commands = data.get('commands', {})
            self.sample_rate = data.get('sample_rate', 16000)
            self.noise_profile = data.get('noise_profile')


class TextToSpeech:
    """
    موتور تبدیل متن به گفتار (Text-to-Speech)
    پشتیبانی از pyttsx3 و SAPI5
    """
    
    def __init__(self, rate: int = 150, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self.is_speaking = False
        self._initialize_engine()
    
    def _initialize_engine(self):
        """راه‌اندازی موتور TTS"""
        if not PYTTSX3_AVAILABLE:
            print("⚠️ pyttsx3 نصب نیست. برای TTS: pip install pyttsx3")
            return
        
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # تنظیم صدای فارسی (اگر موجود باشد)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                voice_name = voice.name.lower()
                if any(name in voice_name for name in ['persian', 'farsi', 'zira']):
                    self.engine.setProperty('voice', voice.id)
                    break
            
            print("✅ TTS راه‌اندازی شد")
        except Exception as e:
            print(f"⚠️ خطا در راه‌اندازی TTS: {e}")
    
    def speak(self, text: str, async_mode: bool = True):
        """تبدیل متن به گفتار"""
        if not self.engine:
            print(f"🔊 [TTS]: {text}")
            return
        
        if not text or not text.strip():
            return
        
        # پاکسازی متن
        text = self._clean_text(text)
        
        if async_mode:
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """اجرای همزمان TTS"""
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ خطا در TTS: {e}")
        finally:
            self.is_speaking = False
    
    def _clean_text(self, text: str) -> str:
        """پاکسازی متن برای گفتار"""
        # تبدیل اعداد لاتین به فارسی
        english_to_persian = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        for eng, per in english_to_persian.items():
            text = text.replace(eng, per)
        
        return text
    
    def set_rate(self, rate: int):
        """تنظیم سرعت گفتار"""
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """تنظیم حجم صدا"""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', volume)
    
    def stop(self):
        """توقف گفتار"""
        if self.engine:
            self.engine.stop()
        self.is_speaking = False


class ImanSpeech:
    """
    کلاس اصلی ماژول گفتار ImanAI
    ترکیب تشخیص فرمان صوتی و تبدیل متن به گفتار
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, model_path: Optional[str] = None):
        """
        راه‌اندازی ماژول گفتار
        
        Args:
            model_path: مسیر ذخیره مدل‌ها
        """
        self.model_path = Path(model_path) if model_path else Path.home() / ".imanailite" / "speech"
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # کامپوننت‌ها
        self.recognizer = VoiceRecognizer()
        self.tts = TextToSpeech()
        
        # تاریخچه
        self.history: List[Dict] = []
        
        # بارگذاری مدل ذخیره شده
        self._load_models()
        
        print(f"🎤 ImanSpeech v{self.VERSION} آماده شد")
        print(f"   مسیر مدل: {self.model_path}")
    
    def add_command(self, key: str, phrases: List[str], category: str = "general",
                    handler: Optional[Callable] = None) -> 'ImanSpeech':
        """
        اضافه کردن فرمان صوتی جدید
        
        Args:
            key: شناسه یکتای فرمان
            phrases: لیست عبارات معادل
            category: دسته‌بندی
            handler: تابع callback که با تشخیص فرمان اجرا می‌شود
        """
        self.recognizer.add_command(key, phrases, category, handler)
        return self
    
    def train_command(self, command_key: str, audio_samples: List[bytes]) -> bool:
        """آموزش یک فرمان با نمونه‌های صوتی"""
        success = self.recognizer.train(command_key, audio_samples)
        if success:
            self._save_models()
        return success
    
    def train_interactive(self, command_key: str, samples_count: int = 5) -> bool:
        """
        آموزش تعاملی فرمان (با ضبط خودکار از میکروفون)
        
        Args:
            command_key: کلید فرمان
            samples_count: تعداد نمونه‌های مورد نیاز
        """
        if command_key not in self.recognizer.commands:
            print(f"❌ فرمان '{command_key}' وجود ندارد. ابتدا از add_command استفاده کنید")
            return False
        
        phrase = self.recognizer.commands[command_key].phrases[0]
        print(f"\n🎤 آموزش فرمان: '{phrase}'")
        print(f"   لطفاً {samples_count} بار این عبارت را بگویید\n")
        
        samples = []
        
        for i in range(samples_count):
            input(f"   نمونه {i+1}/{samples_count}: اینتر را بزنید و بگویید...")
            audio = self.recognizer.record_audio(duration=2.0, timeout=3.0)
            
            if audio:
                samples.append(audio)
                print(f"   ✅ نمونه {i+1} ضبط شد")
            else:
                print(f"   ❌ ضبط ناموفق، دوباره تلاش کنید")
                i -= 1
        
        if len(samples) >= 3:
            return self.train_command(command_key, samples)
        
        return False
    
    def listen_once(self, duration: float = 2.0, timeout: float = 3.0) -> Tuple[Optional[str], float, Optional[str]]:
        """
        یک بار گوش دادن و تشخیص فرمان
        
        Returns:
            (command_key, confidence, detected_phrase)
        """
        audio = self.recognizer.record_audio(duration, timeout)
        if audio:
            command, confidence, phrase = self.recognizer.recognize(audio)
            
            # ثبت در تاریخچه
            if command:
                self.history.append({
                    "command": command,
                    "confidence": confidence,
                    "phrase": phrase,
                    "timestamp": time.time()
                })
                
                if len(self.history) > 100:
                    self.history = self.history[-100:]
            
            return command, confidence, phrase
        
        return None, 0.0, None
    
    def speak(self, text: str, async_mode: bool = True):
        """تبدیل متن به گفتار"""
        self.tts.speak(text, async_mode)
    
    def set_voice(self, rate: Optional[int] = None, volume: Optional[float] = None):
        """تنظیمات صدا"""
        if rate:
            self.tts.set_rate(rate)
        if volume:
            self.tts.set_volume(volume)
    
    def get_stats(self) -> dict:
        """دریافت آمار"""
        return {
            "recognizer": self.recognizer.get_stats(),
            "history_count": len(self.history),
            "tts_available": PYTTSX3_AVAILABLE
        }
    
    def _save_models(self):
        """ذخیره مدل‌ها"""
        model_file = self.model_path / "speech_models.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump({
                'commands': self.recognizer.commands,
                'sample_rate': self.recognizer.sample_rate
            }, f)
    
    def _load_models(self):
        """بارگذاری مدل‌ها"""
        model_file = self.model_path / "speech_models.pkl"
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                self.recognizer.commands = data.get('commands', {})
                print(f"✅ {len(self.recognizer.commands)} فرمان بارگذاری شد")
            except Exception as e:
                print(f"⚠️ خطا در بارگذاری: {e}")
    
    def reset(self):
        """بازنشانی کامل"""
        self.recognizer.commands.clear()
        self.history.clear()
        self._save_models()
        print("🔄 ماژول گفتار بازنشانی شد")