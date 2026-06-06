# ImanAILite/optimizers.py
"""
بهینه‌سازهای مختلف برای آموزش شبکه‌های عصبی
"""

import numpy as np


class Optimizer:
    """کلاس پایه برای همه بهینه‌سازها"""
    def update(self, params, grads):
        raise NotImplementedError


class SGD(Optimizer):
    """Stochastic Gradient Descent - ساده و پایه"""
    def __init__(self, lr=0.001):
        self.lr = lr
    
    def update(self, params, grads):
        for i in range(len(params)):
            params[i] -= self.lr * grads[i]
        return params


class Adam(Optimizer):
    """
    Adam Optimizer (Adaptive Moment Estimation)
    
    مزایا نسبت به SGD:
    - یادگیری سریع‌تر
    - همگرایی بهتر
    - نیاز کمتر به تنظیم دستی lr
    
    Reference: Kingma & Ba, 2015
    """
    
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        """
        Args:
            lr: نرخ یادگیری (Learning Rate)
            beta1: نرخ پوسیدگی برای momentum
            beta2: نرخ پوسیدگی برای RMSprop
            epsilon: مقدار کوچک برای جلوگیری از تقسیم بر صفر
        """
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.t = 0  # شمارنده زمان
        self.m = []  # momentums (اولین گشتاور)
        self.v = []  # velocities (دومین گشتاور)
    
    def update(self, params, grads):
        """
        بروزرسانی پارامترها با استفاده از Adam
        
        Args:
            params: لیست پارامترهای مدل (وزن‌ها و بایاس‌ها)
            grads: لیست گرادیان‌های مربوط به هر پارامتر
        
        Returns:
            params: پارامترهای بروزرسانی شده
        """
        self.t += 1
        
        # مقداردهی اولیه اگر اولین بار است
        if not self.m:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        
        for i, (param, grad) in enumerate(zip(params, grads)):
            # بروزرسانی moments
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad * grad)
            
            # تصحیح بایاس (Bias correction)
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            
            # بروزرسانی پارامتر
            params[i] -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
        
        return params
    
    def reset(self):
        """بازنشانی وضعیت بهینه‌ساز (برای شروع مجدد آموزش)"""
        self.t = 0
        self.m = []
        self.v = []


class RMSprop(Optimizer):
    """RMSprop Optimizer - خوب برای RNN و LSTM"""
    
    def __init__(self, lr=0.001, decay=0.9, epsilon=1e-8):
        self.lr = lr
        self.decay = decay
        self.epsilon = epsilon
        self.cache = []
    
    def update(self, params, grads):
        if not self.cache:
            self.cache = [np.zeros_like(p) for p in params]
        
        for i, (param, grad) in enumerate(zip(params, grads)):
            self.cache[i] = self.decay * self.cache[i] + (1 - self.decay) * (grad * grad)
            params[i] -= self.lr * grad / (np.sqrt(self.cache[i]) + self.epsilon)
        
        return params


class AdamW(Adam):
    """
    AdamW - نسخه بهبود یافته Adam با Weight Decay
    بهتر برای جلوگیری از overfitting
    """
    
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8, weight_decay=0.01):
        super().__init__(lr, beta1, beta2, epsilon)
        self.weight_decay = weight_decay
    
    def update(self, params, grads):
        self.t += 1
        
        if not self.m:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        
        for i, (param, grad) in enumerate(zip(params, grads)):
            # اضافه کردن weight decay به گرادیان
            grad = grad + self.weight_decay * param
            
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad * grad)
            
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            
            params[i] -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
        
        return params