# ImanAILite/activations.py
"""
توابع فعال‌سازی و توابع هزینه برای ImanAILite
نسخه سازگار با پروژه حسابداری پارسه
"""

import numpy as np

DTYPE = np.float32


class Activations:
    """توابع فعال‌سازی (Activation Functions)"""
    
    @staticmethod
    def relu(x):
        """ReLU: max(0, x)"""
        return np.maximum(0, x)

    @staticmethod
    def leaky_relu(x, alpha=0.01):
        """Leaky ReLU: max(alpha*x, x)"""
        return np.where(x > 0, x, alpha * x)

    @staticmethod
    def sigmoid(x):
        """Sigmoid: 1/(1 + e^-x)"""
        x = np.clip(x.astype(DTYPE), -30, 30)
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def tanh(x):
        """Tanh: (e^x - e^-x)/(e^x + e^-x)"""
        return np.tanh(np.clip(x.astype(DTYPE), -10, 10))

    @staticmethod
    def softmax(x):
        """Softmax: e^x / sum(e^x)"""
        x = x.astype(DTYPE)
        x = x - np.max(x, axis=-1, keepdims=True)
        exp_x = np.exp(np.clip(x, -30, 30))
        return exp_x / (np.sum(exp_x, axis=-1, keepdims=True) + 1e-7)

    @staticmethod
    def linear(x):
        """Linear: x (بدون تغییر)"""
        return x
    
    @staticmethod
    def get(name):
        """دریافت تابع فعال‌سازی با نام"""
        activations = {
            'relu': Activations.relu,
            'leaky_relu': Activations.leaky_relu,
            'sigmoid': Activations.sigmoid,
            'tanh': Activations.tanh,
            'softmax': Activations.softmax,
            'linear': Activations.linear
        }
        return activations.get(name, Activations.linear)


class Losses:
    """توابع هزینه (Loss Functions)"""
    
    @staticmethod
    def mse(y_pred, y_true):
        """Mean Squared Error"""
        return np.mean((y_pred - y_true) ** 2)

    @staticmethod
    def mae(y_pred, y_true):
        """Mean Absolute Error"""
        return np.mean(np.abs(y_pred - y_true))

    @staticmethod
    def cross_entropy(y_pred, y_true):
        """Categorical Cross Entropy"""
        eps = 1e-7
        y_pred = np.clip(y_pred, eps, 1 - eps)
        
        if len(y_pred.shape) == 1 or y_pred.shape[1] == 1:
            # Binary Cross Entropy
            y_pred = y_pred.flatten()
            y_true = y_true.flatten()
            return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        else:
            # Categorical Cross Entropy
            return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))

    @staticmethod
    def binary_cross_entropy(y_pred, y_true):
        """Binary Cross Entropy"""
        eps = 1e-7
        y_pred = np.clip(y_pred, eps, 1 - eps)
        y_pred = y_pred.flatten()
        y_true = y_true.flatten()
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    @staticmethod
    def get(name):
        """دریافت تابع هزینه با نام"""
        losses = {
            'mse': Losses.mse,
            'mae': Losses.mae,
            'cross_entropy': Losses.cross_entropy,
            'binary_cross_entropy': Losses.binary_cross_entropy
        }
        return losses.get(name, Losses.mse)