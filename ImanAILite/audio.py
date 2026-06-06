# ImanAILite/audio.py
"""
پردازش سیگنال‌های صوتی برای ImanAI
شامل: MFCC، Spectrogram، تشخیص فرمان صوتی
"""

import numpy as np
from .layers import Dense, Conv2D, MaxPool2D, Flatten, LSTM
from .models import NeuralNetwork


class AudioProcessor:
    """پردازشگر سیگنال صوتی"""
    
    @staticmethod
    def load_audio(file_path, target_sr=16000):
        """بارگذاری فایل صوتی (نیاز به librosa یا scipy)"""
        try:
            import soundfile as sf
            audio, sr = sf.read(file_path)
            # resample if needed
            if sr != target_sr:
                # ساده: downsampling/upsampling با interpolation
                indices = np.linspace(0, len(audio)-1, int(len(audio) * target_sr / sr))
                audio = np.interp(indices, np.arange(len(audio)), audio)
                sr = target_sr
            return audio, sr
        except:
            print("⚠️ Install: pip install soundfile")
            return None, None
    
    @staticmethod
    def mfcc(audio, sr=16000, n_mfcc=13, n_fft=512, hop_length=256):
        """
        تبدیل سیگنال صوتی به MFCC (Mel-frequency cepstral coefficients)
        ورودی برای CNN/RNN
        """
        import scipy.fftpack as fftpack
        
        # تقسیم به فریم‌ها
        frames = []
        for start in range(0, len(audio) - n_fft, hop_length):
            frame = audio[start:start + n_fft]
            # اعمال پنجره هان
            window = np.hanning(len(frame))
            frame = frame * window
            frames.append(frame)
        
        frames = np.array(frames)
        
        # FFT و محاسبه توان
        spectrum = np.abs(fftpack.fft(frames, axis=1))[:, :n_fft//2]
        power = spectrum ** 2
        
        # فیلترهای مل (ساده شده)
        n_filters = 20
        mel_filters = np.random.randn(n_filters, n_fft//2) * 0.1
        
        # اعمال فیلترهای مل
        mel_power = power @ mel_filters.T
        
        # DCT برای MFCC
        mfcc_features = fftpack.dct(np.log(mel_power + 1e-10), axis=1, norm='ortho')
        
        return mfcc_features[:, :n_mfcc]
    
    @staticmethod
    def spectrogram(audio, sr=16000, n_fft=512, hop_length=256):
        """تبدیل صدا به طیف‌نگار (تصویر برای CNN)"""
        import scipy.fftpack as fftpack
        
        frames = []
        for start in range(0, len(audio) - n_fft, hop_length):
            frame = audio[start:start + n_fft]
            window = np.hanning(len(frame))
            frame = frame * window
            frames.append(frame)
        
        frames = np.array(frames)
        spectrum = np.abs(fftpack.fft(frames, axis=1))[:, :n_fft//2]
        
        # نرمال‌سازی برای تصویر
        spectrogram = np.log(spectrum + 1e-10)
        spectrogram = (spectrogram - spectrogram.min()) / (spectrogram.max() - spectrogram.min() + 1e-10)
        
        return spectrogram.reshape(spectrogram.shape[0], spectrogram.shape[1], 1)


class AudioClassifier:
    """تشخیص فرمان صوتی، تشخیص صدا، تشخیص نویز"""
    
    def __init__(self, num_classes, input_length=100, n_mfcc=13):
        self.num_classes = num_classes
        self.input_length = input_length
        self.n_mfcc = n_mfcc
        self.model = None
    
    def build_cnn_model(self):
        """مدل CNN برای پردازش MFCC/طیف‌نگار"""
        self.model = NeuralNetwork("AudioCNN")
        self.model.add(Conv2D(1, 32, 3, padding=1, activation='relu'))
        self.model.add(MaxPool2D(2))
        self.model.add(Conv2D(32, 64, 3, padding=1, activation='relu'))
        self.model.add(MaxPool2D(2))
        self.model.add(Flatten())
        flat_size = 64 * (self.input_length // 4) * (self.n_mfcc // 4)
        self.model.add(Dense(flat_size, 128, 'relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(128, self.num_classes, 'softmax'))
        self.model.compile('cross_entropy', optimizer='adam')
        return self.model
    
    def build_rnn_model(self):
        """مدل RNN برای داده‌های متوالی صوتی"""
        self.model = NeuralNetwork("AudioRNN")
        self.model.add(LSTM(self.n_mfcc, 64, num_layers=2))
        self.model.add(Flatten())
        self.model.add(Dense(64, 32, 'relu'))
        self.model.add(Dense(32, self.num_classes, 'softmax'))
        self.model.compile('cross_entropy', optimizer='adam')
        return self.model
    
    def train(self, X, y, epochs=50, batch_size=16):
        return self.model.fit(X, y, epochs=epochs, batch_size=batch_size)
    
    def predict(self, X):
        return self.model.predict(X)