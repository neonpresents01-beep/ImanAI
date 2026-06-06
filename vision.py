# ImanAILite/vision.py
"""
مدل‌های پیشرفته بینایی ماشین
شامل: ResNet ساده، Data Augmentation
"""

import numpy as np
from .models import NeuralNetwork
from .layers import Conv2D, MaxPool2D, Dense, Flatten, BatchNorm, Dropout


class DataAugmentation:
    """افزایش داده برای تصاویر (جلوگیری از overfitting)"""
    
    @staticmethod
    def random_rotate(image, angle_range=(-15, 15)):
        """چرخش تصادفی تصویر"""
        import scipy.ndimage as ndimage
        angle = np.random.uniform(angle_range[0], angle_range[1])
        return ndimage.rotate(image, angle, reshape=False, order=1)
    
    @staticmethod
    def random_flip(image, horizontal=True, vertical=False):
        """آینه کردن تصادفی"""
        if horizontal and np.random.random() > 0.5:
            image = np.fliplr(image)
        if vertical and np.random.random() > 0.5:
            image = np.flipud(image)
        return image
    
    @staticmethod
    def random_brightness(image, delta=0.2):
        """تغییر روشنایی تصادفی"""
        return np.clip(image + np.random.uniform(-delta, delta), 0, 1)
    
    @staticmethod
    def random_shift(image, max_shift=4):
        """جابجایی تصادفی"""
        shift_x = np.random.randint(-max_shift, max_shift)
        shift_y = np.random.randint(-max_shift, max_shift)
        return np.roll(image, shift_x, axis=0).roll(shift_y, axis=1)
    
    @staticmethod
    def augment_batch(images, labels, augment_prob=0.5):
        """اعمال augmentation روی یک بچ"""
        augmented_images = []
        augmented_labels = []
        
        for img, label in zip(images, labels):
            augmented_images.append(img)
            augmented_labels.append(label)
            
            if np.random.random() < augment_prob:
                # یک augmentation جدید اضافه کن
                new_img = img.copy()
                new_img = DataAugmentation.random_rotate(new_img)
                new_img = DataAugmentation.random_flip(new_img)
                new_img = DataAugmentation.random_brightness(new_img)
                augmented_images.append(new_img)
                augmented_labels.append(label)
        
        return np.array(augmented_images), np.array(augmented_labels)


class SimpleResNet:
    """ResNet ساده برای تصاویر کوچک (32x32, 64x64)"""
    
    def __init__(self, input_shape, num_classes, depth=18):
        self.input_shape = input_shape  # (h, w, c)
        self.num_classes = num_classes
        self.depth = depth
        self.model = None
    
    def _residual_block(self, model, filters, stride=1):
        """بلوک residual با skip connection"""
        shortcut = model.layers[-1].forward if model.layers else None
        
        model.add(Conv2D(filters, filters, 3, stride=stride, padding=1, activation='relu'))
        model.add(BatchNorm(filters))
        model.add(Conv2D(filters, filters, 3, padding=1, activation='linear'))
        model.add(BatchNorm(filters))
        
        if shortcut:
            # اضافه کردن skip connection
            pass  # برای پیاده‌سازی ساده
        
        return model
    
    def build(self):
        """ساخت معماری ResNet"""
        h, w, c = self.input_shape
        
        self.model = NeuralNetwork(f"ResNet{self.depth}")
        
        # ورودی
        self.model.add(Conv2D(c, 64, 7, stride=2, padding=3, activation='relu'))
        self.model.add(MaxPool2D(3, stride=2))
        
        # Residual blocks (ساده شده)
        self.model.add(Conv2D(64, 64, 3, padding=1, activation='relu'))
        self.model.add(BatchNorm(64))
        self.model.add(Conv2D(64, 64, 3, padding=1, activation='relu'))
        self.model.add(BatchNorm(64))
        
        self.model.add(Conv2D(64, 128, 3, stride=2, padding=1, activation='relu'))
        self.model.add(BatchNorm(128))
        self.model.add(Conv2D(128, 128, 3, padding=1, activation='relu'))
        self.model.add(BatchNorm(128))
        
        self.model.add(Conv2D(128, 256, 3, stride=2, padding=1, activation='relu'))
        self.model.add(BatchNorm(256))
        
        self.model.add(Flatten())
        
        # مقداردهی دقیق flat_size
        flat_size = 256 * (h // 8) * (w // 8)
        self.model.add(Dense(flat_size, 512, 'relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(512, self.num_classes, 'softmax'))
        
        self.model.compile('cross_entropy', optimizer='adam')
        return self.model
    
    def train(self, X, y, epochs=50, batch_size=32, use_augmentation=True):
        """آموزش با قابلیت Data Augmentation"""
        if use_augmentation:
            X, y = DataAugmentation.augment_batch(X, y)
        
        return self.model.fit(X, y, epochs=epochs, batch_size=batch_size)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def save(self, path):
        self.model.save(path)
    
    def load(self, path):
        self.model = NeuralNetwork().load(path)


# کلاس Embedding ساده
class Embedding:
    """لایه Embedding برای کلمات"""
    
    def __init__(self, vocab_size, embed_dim, lr=0.001):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.lr = lr
        
        scale = np.sqrt(1.0 / vocab_size)
        self.weights = (np.random.randn(vocab_size, embed_dim) * scale).astype(np.float32)
        self.dweights = None
        self.last_input = None
    
    def forward(self, x, training=True):
        self.last_input = x
        return self.weights[x]
    
    def backward(self, grad):
        self.dweights = np.zeros_like(self.weights)
        for i, idx in enumerate(self.last_input.flatten()):
            self.dweights[idx] += grad[i]
        return None
    
    def update(self, lr=None):
        if lr is None:
            lr = self.lr
        if self.dweights is not None:
            self.weights -= lr * self.dweights
            