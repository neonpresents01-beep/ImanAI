# ImanAILite/utils.py
"""
ابزارهای کمکی برای آموزش مدل‌ها
شامل: Gradient Clipping, Learning Rate Scheduler, Model Checkpoint
"""

import numpy as np
import copy


def gradient_clipping(grads, max_norm=1.0):
    """
    Gradient Clipping - جلوگیری از انفجار گرادیان در 32-bit
    
    وقتی گرادیان‌ها خیلی بزرگ می‌شن، مدل ناپایدار میشه.
    این تابع اونها رو به محدوده امن محدود می‌کنه.
    
    Args:
        grads: لیست گرادیان‌ها (از لایه‌های مختلف)
        max_norm: حداکثر نرم مجاز
    
    Returns:
        grads: گرادیان‌های کلیپ شده
    """
    # محاسبه نرم کل گرادیان‌ها
    total_norm = 0.0
    for g in grads:
        if g is not None:
            total_norm += np.sum(g ** 2)
    total_norm = np.sqrt(total_norm)
    
    # اگر از حد مجاز بیشتر بود، مقیاس بندی کن
    if total_norm > max_norm:
        clip_coef = max_norm / (total_norm + 1e-6)
        for i in range(len(grads)):
            if grads[i] is not None:
                grads[i] = grads[i] * clip_coef
    
    return grads


class LearningRateScheduler:
    """
    تنظیم کننده نرخ یادگیری در حین آموزش
    
    انواع استراتژی‌ها:
    - step: کاهش پله‌ای
    - exponential: کاهش نمایی
    - plateau: کاهش وقتی loss ثابت موند
    """
    
    def __init__(self, optimizer, initial_lr=0.001, strategy='step', 
                 step_size=30, gamma=0.1, patience=10, factor=0.5):
        """
        Args:
            optimizer: بهینه‌ساز مدل
            initial_lr: نرخ یادگیری اولیه
            strategy: استراتژی ('step', 'exponential', 'plateau')
            step_size: تعداد epoch برای کاهش (در استراتژی step)
            gamma: ضریب کاهش
            patience: تعداد epoch برای انتظار (در استراتژی plateau)
            factor: ضریب کاهش در plateau
        """
        self.optimizer = optimizer
        self.initial_lr = initial_lr
        self.strategy = strategy
        self.step_size = step_size
        self.gamma = gamma
        self.patience = patience
        self.factor = factor
        self.current_lr = initial_lr
        self.epoch = 0
        self.best_loss = float('inf')
        self.wait_count = 0
    
    def step(self, epoch=None, current_loss=None):
        """
        بروزرسانی نرخ یادگیری بعد از هر epoch
        
        Args:
            epoch: شماره epoch (اگر None باشه، از internal counter استفاده می‌کنه)
            current_loss: loss فعلی (برای استراتژی plateau لازمه)
        
        Returns:
            learning_rate جدید
        """
        if epoch is not None:
            self.epoch = epoch
        else:
            self.epoch += 1
        
        new_lr = self.current_lr
        
        if self.strategy == 'step':
            # کاهش پله‌ای هر step_size epoch
            if self.epoch % self.step_size == 0 and self.epoch > 0:
                new_lr = self.current_lr * self.gamma
        
        elif self.strategy == 'exponential':
            # کاهش نمایی در هر epoch
            new_lr = self.initial_lr * (self.gamma ** self.epoch)
        
        elif self.strategy == 'plateau':
            # کاهش وقتی loss بهبود پیدا نکرد
            if current_loss is not None:
                if current_loss < self.best_loss - 1e-4:
                    self.best_loss = current_loss
                    self.wait_count = 0
                else:
                    self.wait_count += 1
                
                if self.wait_count >= self.patience:
                    new_lr = self.current_lr * self.factor
                    self.wait_count = 0
        
        # بروزرسانی نرخ یادگیری در بهینه‌ساز
        if new_lr != self.current_lr:
            self.current_lr = new_lr
            if hasattr(self.optimizer, 'lr'):
                self.optimizer.lr = self.current_lr
            print(f"📉 Learning rate changed to: {self.current_lr:.6f}")
        
        return self.current_lr
    
    def get_lr(self):
        """دریافت نرخ یادگیری فعلی"""
        return self.current_lr
    
    def reset(self):
        """بازنشانی به حالت اولیه"""
        self.epoch = 0
        self.current_lr = self.initial_lr
        self.best_loss = float('inf')
        self.wait_count = 0


class ModelCheckpoint:
    """
    ذخیره خودکار بهترین مدل در حین آموزش
    
    قابلیت‌ها:
    - ذخیره فقط وقتی loss بهتر شد
    - نگهداری چند نسخه آخر
    - ذخیره دوره‌ای
    """
    
    def __init__(self, save_dir='checkpoints', monitor='val_loss', 
                 save_best_only=True, save_weights_only=False,
                 period=5, mode='min'):
        """
        Args:
            save_dir: مسیر ذخیره فایل‌ها
            monitor: معیار پایش ('loss', 'val_loss', 'accuracy')
            save_best_only: فقط بهترین مدل رو ذخیره کن
            save_weights_only: فقط وزن‌ها رو ذخیره کن (نه کل مدل)
            period: ذخیره دوره‌ای هر چند epoch
            mode: 'min' برای loss، 'max' برای accuracy
        """
        self.save_dir = save_dir
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.mode = mode
        
        self.best_value = float('inf') if mode == 'min' else -float('inf')
        self.best_epoch = -1
        self.checkpoints = []
        
        # ایجاد پوشه اگر وجود نداشت
        import os
        os.makedirs(save_dir, exist_ok=True)
    
    def on_epoch_end(self, epoch, model, current_value):
        """
        بررسی و ذخیره مدل در پایان هر epoch
        
        Args:
            epoch: شماره epoch
            model: مدل مورد نظر
            current_value: مقدار فعلی معیار (loss یا accuracy)
        
        Returns:
            bool: آیا مدل ذخیره شد؟
        """
        saved = False
        
        # بررسی اینکه آیا بهتر شده
        is_best = False
        if self.mode == 'min':
            is_best = current_value < self.best_value
        else:
            is_best = current_value > self.best_value
        
        # ذخیره اگر بهتر شد و save_best_only فعال باشه
        if is_best:
            self.best_value = current_value
            self.best_epoch = epoch
            self._save_model(epoch, model, 'best')
            saved = True
        
        # ذخیره دوره‌ای
        if not self.save_best_only and (epoch + 1) % self.period == 0:
            self._save_model(epoch, model, f'epoch_{epoch+1}')
            saved = True
        
        return saved
    
    def _save_model(self, epoch, model, suffix):
        """ذخیره مدل در فایل"""
        import pickle
        import os
        
        filename = f"{model.name}_{suffix}.pkl"
        filepath = os.path.join(self.save_dir, filename)
        
        if self.save_weights_only:
            # فقط وزن‌ها رو ذخیره کن
            weights = self._get_weights(model)
            with open(filepath, 'wb') as f:
                pickle.dump(weights, f)
        else:
            # کل مدل رو ذخیره کن
            model.save(filepath)
        
        self.checkpoints.append(filepath)
        print(f"💾 Checkpoint saved: {filepath}")
        
        # حذف checkpointهای قدیمی (فقط ۵ تا آخر رو نگه دار)
        if len(self.checkpoints) > 5:
            old_file = self.checkpoints.pop(0)
            if os.path.exists(old_file):
                os.remove(old_file)
    
    def _get_weights(self, model):
        """استخراج وزن‌ها از مدل"""
        weights = []
        for layer in model.layers:
            if hasattr(layer, 'W'):
                weights.append(layer.W.copy())
                weights.append(layer.b.copy())
            elif hasattr(layer, 'gamma'):
                weights.append(layer.gamma.copy())
                weights.append(layer.beta.copy())
        return weights
    
    def load_best(self, model):
        """بارگذاری بهترین مدل ذخیره شده"""
        best_path = os.path.join(self.save_dir, f"{model.name}_best.pkl")
        if os.path.exists(best_path):
            model.load(best_path)
            print(f"📂 Best model loaded from {best_path}")
            return True
        return False