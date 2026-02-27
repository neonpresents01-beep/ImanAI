#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ایمان حسابداری - ImanAccounting
نسخه ۸.۰.۰ - با ImanAILight داخلی
سینا جان - ۱۴۰۳
"""

import sys
import os
import json
import hashlib
import sqlite3
import importlib.util
import inspect
import shutil
import zipfile
import socket
import platform
import uuid
import base64
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# ====================== ImanAILight (داخلی) ======================

class Tensor:
    """تانسور اختصاصی ImanAILight"""
    
    def __init__(self, data, shape=None):
        self.data = data if isinstance(data, list) else [data]
        self.shape = shape if shape else (len(self.data),)
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Tensor([x + other for x in self.data])
        return Tensor([a + b for a, b in zip(self.data, other.data)])
    
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Tensor([x - other for x in self.data])
        return Tensor([a - b for a, b in zip(self.data, other.data)])
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Tensor([x * other for x in self.data])
        return Tensor([a * b for a, b in zip(self.data, other.data)])
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Tensor([x / other for x in self.data])
        return Tensor([a / b for a, b in zip(self.data, other.data)])
    
    def sum(self):
        return sum(self.data)
    
    def mean(self):
        return sum(self.data) / len(self.data)
    
    def tolist(self):
        return self.data


class ActivationFunctions:
    """توابع فعالسازی"""
    
    @staticmethod
    def relu(x):
        return max(0, x)
    
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))
    
    @staticmethod
    def tanh(x):
        return math.tanh(x)
    
    @staticmethod
    def linear(x):
        return x


class Dense:
    """لایه تمام متصل"""
    
    def __init__(self, input_dim, output_dim, activation='relu'):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.activation = activation
        self.weights = Tensor([random.uniform(-1, 1) for _ in range(input_dim * output_dim)])
        self.bias = Tensor([random.uniform(-1, 1) for _ in range(output_dim)])
        self.input_data = None
    
    def forward(self, x):
        self.input_data = x
        # ضرب ماتریسی ساده
        result = []
        for i in range(self.output_dim):
            s = 0
            for j in range(self.input_dim):
                s += x.data[j] * self.weights.data[i * self.input_dim + j]
            s += self.bias.data[i]
            
            if self.activation == 'relu':
                s = ActivationFunctions.relu(s)
            elif self.activation == 'sigmoid':
                s = ActivationFunctions.sigmoid(s)
            elif self.activation == 'tanh':
                s = ActivationFunctions.tanh(s)
            
            result.append(s)
        
        return Tensor(result)


class Sequential:
    """مدل ترتیبی"""
    
    def __init__(self, name='model'):
        self.name = name
        self.layers = []
    
    def add(self, layer):
        self.layers.append(layer)
    
    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def predict(self, x):
        if not isinstance(x, Tensor):
            x = Tensor(x)
        return self.forward(x)


class SimpleAI:
    """هوش مصنوعی ساده برای تحلیل"""
    
    @staticmethod
    def predict_next(data):
        """پیش‌بینی مقدار بعدی با میانگین متحرک"""
        if len(data) < 3:
            return sum(data) / len(data) if data else 0
        return (data[-1] + data[-2] + data[-3]) / 3
    
    @staticmethod
    def detect_anomaly(data, value):
        """تشخیص ناهنجاری با انحراف معیار"""
        if len(data) < 5:
            return False
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std = math.sqrt(variance)
        return abs(value - mean) > 3 * std
    
    @staticmethod
    def trend_analysis(data):
        """تحلیل روند"""
        if len(data) < 2:
            return "نامشخص"
        if data[-1] > data[0]:
            return "صعودی 📈"
        elif data[-1] < data[0]:
            return "نزولی 📉"
        else:
            return "ثابت ➡️"


# ====================== اطلاعات برند ======================

APP_NAME = "ایمان حسابداری"
APP_NAME_EN = "ImanAccounting"
APP_VERSION = "8.0.0"
APP_AUTHOR = "سینا"
APP_SLOGAN = "حساب‌هایت رو به ایمان بسپار"
APP_WEBSITE = "iman-ai.ir"
APP_EMAIL = "info@iman-ai.ir"
APP_TELEGRAM = "@ImanAI2026"

ADMIN_SECRET_KEY = "Iman@Admin@2024#SuperSecret"

THEMES = {
    "dark": {
        'name': 'تیره',
        'primary': '#00a8ff',
        'secondary': '#192a56',
        'background': '#2c3a47',
        'card_bg': '#34495e',
        'text': '#ecf0f1',
        'text_secondary': '#bdc3c7',
        'border': '#2980b9',
        'success': '#00b894',
        'danger': '#d63031',
        'warning': '#f39c12',
        'info': '#0984e3',
        'hover': '#74b9ff'
    },
    "light": {
        'name': 'روشن',
        'primary': '#0984e3',
        'secondary': '#74b9ff',
        'background': '#dfe6e9',
        'card_bg': '#ffffff',
        'text': '#2d3436',
        'text_secondary': '#636e72',
        'border': '#b2bec3',
        'success': '#00cec9',
        'danger': '#ff7675',
        'warning': '#fdcb6e',
        'info': '#0984e3',
        'hover': '#00a8ff'
    }
}


# ====================== کلاس ScreenOptimizer ======================

class ScreenOptimizer:
    """بهینه‌سازی برای همه صفحه‌ها"""
    
    def __init__(self):
        self.screen = QDesktopWidget().screenGeometry()
        self.width = self.screen.width()
        self.height = self.screen.height()
        
        if self.width <= 1024:
            self.scale = 0.7
        elif self.width <= 1280:
            self.scale = 0.8
        elif self.width <= 1366:
            self.scale = 0.9
        else:
            self.scale = 1.0
    
    def get_size(self, base_size):
        return int(base_size * self.scale)
    
    def get_font_size(self, base=10):
        sizes = {
            0.7: max(8, int(base * 0.8)),
            0.8: max(9, int(base * 0.9)),
            0.9: int(base * 1.0),
            1.0: int(base * 1.1)
        }
        return sizes.get(self.scale, base)
    
    def get_margin(self, base=8):
        return int(base * self.scale)
    
    def get_spacing(self, base=10):
        return int(base * self.scale)
    
    def get_icon_size(self, base=24):
        return int(base * self.scale)
    
    def get_card_size(self, base=100):
        return int(base * self.scale)
    
    def get_button_height(self, base=40):
        return int(base * self.scale)


# ====================== کلاس LicenseManager ======================

class LicenseType(Enum):
    FREE = "رایگان"
    TRIAL = "آزمایشی"
    PRO = "حرفه‌ای"
    ADMIN = "ادمین"
    SCHOOL = "مدرسه"


class LicenseManager:
    """مدیریت لایسنس"""
    
    def __init__(self):
        self.license_type = LicenseType.FREE
        self.license_key = None
        self.license_data = None
        self.expiry_date = None
        self.is_admin = False
        self.is_school = False
        self.hardware_id = self.get_hardware_id()
        self.license_file = "license.lic"
        self.admin_file = "admin.lic"
        self.school_file = "school.lic"
        self.pro_file = "pro.lic"
        self.trial_file = "trial.lic"
        self.load_license()
    
    def get_hardware_id(self) -> str:
        try:
            mac = uuid.getnode()
            hostname = socket.gethostname()
            processor = platform.processor()
            hw_string = f"{mac}-{hostname}-{processor}"
            return hashlib.sha256(hw_string.encode()).hexdigest()[:32]
        except:
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
    
    def generate_school_license(self, hwid: str) -> str:
        data = {
            'hwid': hwid,
            'type': 'SCHOOL',
            'created': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=3650)).isoformat(),
            'school': 'مدرسه'
        }
        json_data = json.dumps(data)
        key = hashlib.sha256(APP_NAME.encode()).hexdigest()
        license_key = base64.b64encode(f"{key}:{json_data}".encode()).decode()
        checksum = hashlib.md5(license_key.encode()).hexdigest()[:8]
        return f"{license_key}-{checksum}"
    
    def generate_admin_license(self, hwid: str) -> str:
        data = {
            'hwid': hwid,
            'type': 'ADMIN',
            'created': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=3650)).isoformat(),
            'secret': ADMIN_SECRET_KEY
        }
        json_data = json.dumps(data)
        key = hashlib.sha256(ADMIN_SECRET_KEY.encode()).hexdigest()
        license_key = base64.b64encode(f"{key}:{json_data}".encode()).decode()
        checksum = hashlib.md5(license_key.encode()).hexdigest()[:8]
        return f"{license_key}-{checksum}"
    
    def generate_user_license(self, hwid: str, license_type: str, days: int = 365) -> str:
        data = {
            'hwid': hwid,
            'type': license_type,
            'created': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=days)).isoformat(),
            'random': hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        }
        json_data = json.dumps(data)
        key = hashlib.sha256(APP_NAME.encode()).hexdigest()
        license_key = base64.b64encode(f"{key}:{json_data}".encode()).decode()
        checksum = hashlib.md5(license_key.encode()).hexdigest()[:8]
        return f"{license_key}-{checksum}"
    
    def validate_license(self, license_key: str) -> Tuple[bool, str, LicenseType]:
        try:
            if '-' not in license_key:
                return False, "فرمت لایسنس نامعتبر", LicenseType.FREE
            
            key_part, checksum = license_key.rsplit('-', 1)
            
            if hashlib.md5(key_part.encode()).hexdigest()[:8] != checksum:
                return False, "لایسنس دستکاری شده", LicenseType.FREE
            
            decoded = base64.b64decode(key_part).decode()
            separator = decoded.find(':')
            if separator == -1:
                return False, "فرمت نامعتبر", LicenseType.FREE
            
            json_data = decoded[separator+1:]
            data = json.loads(json_data)
            
            if data['hwid'] != self.hardware_id:
                return False, "این لایسنس برای این کامپیوتر نیست", LicenseType.FREE
            
            if data['type'] == 'ADMIN':
                if data.get('secret') != ADMIN_SECRET_KEY:
                    return False, "لایسنس ادمین نامعتبر", LicenseType.FREE
                self.is_admin = True
                return True, "لایسنس ادمین فعال شد", LicenseType.ADMIN
            
            if data['type'] == 'SCHOOL':
                self.is_school = True
                return True, "لایسنس مدرسه فعال شد", LicenseType.SCHOOL
            
            expiry = datetime.fromisoformat(data['expiry'])
            if expiry < datetime.now():
                return False, f"لایسنس منقضی شده", LicenseType.FREE
            
            if data['type'] == 'PRO':
                return True, "لایسنس حرفه‌ای فعال شد", LicenseType.PRO
            elif data['type'] == 'TRIAL':
                return True, "لایسنس آزمایشی فعال شد", LicenseType.TRIAL
            else:
                return True, "لایسنس فعال شد", LicenseType.FREE
                
        except Exception as e:
            return False, f"خطا: {str(e)}", LicenseType.FREE
    
    def load_license(self):
        license_files = [
            (self.school_file, LicenseType.SCHOOL, True),
            (self.admin_file, LicenseType.ADMIN, True),
            (self.pro_file, LicenseType.PRO, False),
            (self.trial_file, LicenseType.TRIAL, False),
            (self.license_file, LicenseType.FREE, False)
        ]
        
        for filename, license_type, is_special in license_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        license_key = f.read().strip()
                    valid, msg, ltype = self.validate_license(license_key)
                    if valid:
                        self.license_type = ltype
                        self.license_key = license_key
                        if is_special:
                            if license_type == LicenseType.ADMIN:
                                self.is_admin = True
                            elif license_type == LicenseType.SCHOOL:
                                self.is_school = True
                        print(f"✅ {msg}")
                        return
                except:
                    pass
        
        print("ℹ️ نسخه رایگان فعال شد")
        self.license_type = LicenseType.FREE
    
    def save_license(self, license_key: str, license_type: LicenseType):
        if license_type == LicenseType.ADMIN:
            filename = self.admin_file
        elif license_type == LicenseType.SCHOOL:
            filename = self.school_file
        elif license_type == LicenseType.PRO:
            filename = self.pro_file
        elif license_type == LicenseType.TRIAL:
            filename = self.trial_file
        else:
            filename = self.license_file
        
        try:
            with open(filename, 'w') as f:
                f.write(license_key)
            return True
        except:
            return False


# ====================== کلاس DatabaseManager ======================

class Account:
    def __init__(self, code: str, name: str, type: str, parent_id: int = None):
        self.id = None
        self.code = code
        self.name = name
        self.type = type
        self.parent_id = parent_id
        self.balance = 0.0
        self.is_active = True
        self.created_at = datetime.now()


class Transaction:
    def __init__(self, date: datetime, description: str, amount: float, 
                 type: str, debit_account_id: int, credit_account_id: int):
        self.id = None
        self.number = self.generate_number()
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.debit_account_id = debit_account_id
        self.credit_account_id = credit_account_id
        self.is_verified = True
        self.created_at = datetime.now()
    
    @staticmethod
    def generate_number() -> str:
        return f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}"


class DatabaseManager:
    def __init__(self, db_path: str = "iman_accounting.db"):
        self.db_path = db_path
        self.accounts = []
        self.transactions = []
        self.ai = SimpleAI()
        self.init_database()
        self.load_data()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    parent_id INTEGER,
                    balance REAL DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT UNIQUE NOT NULL,
                    date DATE NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    debit_account_id INTEGER NOT NULL,
                    credit_account_id INTEGER NOT NULL,
                    is_verified INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (debit_account_id) REFERENCES accounts(id),
                    FOREIGN KEY (credit_account_id) REFERENCES accounts(id)
                )
            ''')
            
            cursor.execute("SELECT COUNT(*) FROM accounts")
            count = cursor.fetchone()[0]
            
            if count == 0:
                default_accounts = [
                    ('1001', 'وجه نقد', 'asset'),
                    ('1002', 'بانک', 'asset'),
                    ('1101', 'حساب‌های دریافتنی', 'asset'),
                    ('2001', 'حساب‌های پرداختنی', 'liability'),
                    ('3001', 'سرمایه', 'equity'),
                    ('4001', 'فروش', 'revenue'),
                    ('5001', 'هزینه‌ها', 'expense'),
                ]
                
                for code, name, type_ in default_accounts:
                    cursor.execute('''
                        INSERT INTO accounts (code, name, type)
                        VALUES (?, ?, ?)
                    ''', (code, name, type_))
                
                conn.commit()
    
    def load_data(self):
        try:
            accounts_data = self.execute_query("SELECT * FROM accounts WHERE is_active = 1 ORDER BY code")
            
            for acc in accounts_data:
                account = Account(acc[1], acc[2], acc[3])
                account.id = acc[0]
                account.balance = acc[4] if acc[4] is not None else 0.0
                account.parent_id = acc[5]
                self.accounts.append(account)
            
            trans_data = self.execute_query(
                "SELECT * FROM transactions ORDER BY date DESC LIMIT 100"
            )
            
            for trans in trans_data:
                date = datetime.strptime(trans[2], '%Y-%m-%d')
                transaction = Transaction(
                    date, trans[3] or '', trans[5], trans[4],
                    trans[6], trans[7]
                )
                transaction.id = trans[0]
                transaction.number = trans[1]
                transaction.is_verified = bool(trans[8])
                self.transactions.append(transaction)
            
        except Exception as e:
            print(f"خطا در بارگذاری: {e}")
    
    def execute_query(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def get_all_accounts(self) -> List[Account]:
        if len(self.accounts) == 0:
            self.load_data()
        return self.accounts
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        for acc in self.accounts:
            if acc.id == account_id:
                return acc
        return None
    
    def add_account(self, account: Account) -> bool:
        try:
            account_id = self.execute_insert('''
                INSERT INTO accounts (code, name, type, parent_id)
                VALUES (?, ?, ?, ?)
            ''', (account.code, account.name, account.type, account.parent_id))
            
            account.id = account_id
            self.accounts.append(account)
            return True
        except:
            return False
    
    def update_account_balance(self, account_id: int, amount: float):
        for acc in self.accounts:
            if acc.id == account_id:
                acc.balance += amount
                self.execute_update(
                    "UPDATE accounts SET balance = ? WHERE id = ?",
                    (acc.balance, account_id)
                )
                break
    
    def add_transaction(self, transaction: Transaction) -> bool:
        try:
            trans_id = self.execute_insert('''
                INSERT INTO transactions 
                (number, date, description, type, amount, debit_account_id, credit_account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.number,
                transaction.date.strftime('%Y-%m-%d'),
                transaction.description,
                transaction.type,
                transaction.amount,
                transaction.debit_account_id,
                transaction.credit_account_id
            ))
            
            transaction.id = trans_id
            self.transactions.insert(0, transaction)
            
            self.update_account_balance(transaction.debit_account_id, transaction.amount)
            self.update_account_balance(transaction.credit_account_id, -transaction.amount)
            
            return True
        except Exception as e:
            print(f"خطا: {e}")
            return False
    
    def get_all_transactions(self, limit: int = 100) -> List[Transaction]:
        return sorted(self.transactions, key=lambda x: x.date, reverse=True)[:limit]
    
    def get_total_balance(self) -> float:
        total = 0
        for acc in self.accounts:
            if acc.type == 'asset':
                total += acc.balance
        return total
    
    def get_today_income_expense(self) -> Tuple[float, float]:
        today = datetime.now().date()
        income = 0
        expense = 0
        
        for trans in self.transactions:
            if trans.date.date() == today:
                if trans.type == 'درآمد':
                    income += trans.amount
                elif trans.type == 'هزینه':
                    expense += trans.amount
        
        return income, expense
    
    # ====================== قابلیت‌های هوش مصنوعی ======================
    
    def predict_next_expense(self):
        """پیش‌بینی هزینه ماه آینده"""
        expenses = [t.amount for t in self.transactions if t.type == "هزینه"]
        return self.ai.predict_next(expenses)
    
    def detect_anomaly(self, transaction):
        """تشخیص تراکنش مشکوک"""
        expenses = [t.amount for t in self.transactions if t.type == "هزینه"]
        return self.ai.detect_anomaly(expenses, transaction.amount)
    
    def trend_analysis(self):
        """تحلیل روند هزینه‌ها"""
        expenses = [t.amount for t in self.transactions if t.type == "هزینه"]
        return self.ai.trend_analysis(expenses)


# ====================== کلاس ThemeManager ======================

class ThemeManager:
    def __init__(self, optimizer: ScreenOptimizer):
        self.optimizer = optimizer
        self.themes = THEMES
        self.current_theme_name = "dark"
        self.current_theme = self.themes[self.current_theme_name]
        self.settings_file = "theme_settings.json"
        self.load_settings()
    
    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.current_theme_name = data.get("theme", "dark")
                self.current_theme = self.themes[self.current_theme_name]
        except:
            pass
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({"theme": self.current_theme_name}, f)
        except:
            pass
    
    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            self.save_settings()
    
    def get_style(self):
        theme = self.current_theme
        return f"""
            QMainWindow {{
                background-color: {theme['background']};
            }}
            QMenuBar {{
                background-color: {theme['secondary']};
                color: {theme['text']};
                border: none;
                font-size: {self.optimizer.get_font_size(10)}px;
                padding: {self.optimizer.get_margin(5)}px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: {self.optimizer.get_margin(8)}px {self.optimizer.get_margin(12)}px;
            }}
            QMenuBar::item:selected {{
                background-color: {theme['primary']};
                border-radius: {self.optimizer.get_margin(4)}px;
            }}
            QMenu {{
                background-color: {theme['card_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QMenu::item:selected {{
                background-color: {theme['primary']};
                color: white;
            }}
            QTabWidget::pane {{
                background-color: {theme['background']};
                border: none;
            }}
            QTabBar::tab {{
                background-color: {theme['card_bg']};
                color: {theme['text']};
                padding: {self.optimizer.get_margin(8)}px {self.optimizer.get_margin(16)}px;
                margin-right: 2px;
                border: 1px solid {theme['border']};
                border-bottom: none;
                border-top-left-radius: {self.optimizer.get_margin(6)}px;
                border-top-right-radius: {self.optimizer.get_margin(6)}px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['primary']};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme['hover']};
            }}
            QStatusBar {{
                background-color: {theme['secondary']};
                color: {theme['text']};
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QToolBar {{
                background-color: {theme['card_bg']};
                border: none;
                spacing: {self.optimizer.get_spacing(5)}px;
                padding: {self.optimizer.get_margin(5)}px;
            }}
        """


# ====================== کلاس StatCard ======================

class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, color: str, optimizer: ScreenOptimizer, theme: dict):
        super().__init__()
        self.optimizer = optimizer
        self.theme = theme
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: {self.optimizer.get_margin(10)}px;
                padding: {self.optimizer.get_margin(10)}px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(
            self.optimizer.get_margin(15),
            self.optimizer.get_margin(10),
            self.optimizer.get_margin(15),
            self.optimizer.get_margin(10)
        )
        layout.setSpacing(self.optimizer.get_spacing(10))
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: {self.optimizer.get_icon_size(30)}px; background: transparent; color: white;")
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(12)}px; color: rgba(255,255,255,0.8); background: transparent;")
        text_layout.addWidget(title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(20)}px; font-weight: bold; color: white; background: transparent;")
        text_layout.addWidget(self.value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedHeight(self.optimizer.get_card_size(100))
    
    def update_value(self, value: str):
        self.value_label.setText(value)


# ====================== کلاس AIDashboard ======================

class AIDashboard(QDialog):
    """داشبورد هوش مصنوعی"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("🤖 داشبورد هوش مصنوعی")
        self.resize(self.optimizer.get_size(600), self.optimizer.get_size(500))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['background']};
            }}
            QGroupBox {{
                color: {self.theme['text']};
                border: 2px solid {self.theme['primary']};
                border-radius: {self.optimizer.get_margin(5)}px;
                margin-top: {self.optimizer.get_margin(10)}px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.optimizer.get_margin(10)}px;
                padding: 0 {self.optimizer.get_margin(5)}px 0 {self.optimizer.get_margin(5)}px;
                color: {self.theme['primary']};
            }}
            QLabel {{
                color: {self.theme['text']};
            }}
            QPushButton {{
                background-color: {self.theme['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin(5)}px;
                padding: {self.optimizer.get_margin(8)}px;
                font-weight: bold;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing(15))
        
        title = QLabel("🤖 داشبورد هوش مصنوعی")
        title.setStyleSheet(f"font-size: {self.optimizer.get_font_size(18)}px; font-weight: bold; color: {self.theme['primary']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # پیش‌بینی هزینه
        pred_group = QGroupBox("📊 پیش‌بینی هزینه")
        pred_layout = QVBoxLayout()
        
        expenses = [t.amount for t in self.db.get_all_transactions() if t.type == "هزینه"]
        if expenses:
            pred = self.db.predict_next_expense()
            trend = self.db.trend_analysis()
            
            pred_layout.addWidget(QLabel(f"میانگین هزینه‌ها: {sum(expenses)/len(expenses):,.0f}"))
            pred_layout.addWidget(QLabel(f"🔮 پیش‌بینی ماه آینده: {pred:,.0f}"))
            pred_layout.addWidget(QLabel(f"📈 روند: {trend}"))
        else:
            pred_layout.addWidget(QLabel("داده کافی برای پیش‌بینی وجود ندارد"))
        
        pred_group.setLayout(pred_layout)
        layout.addWidget(pred_group)
        
        # تشخیص ناهنجاری
        anomaly_group = QGroupBox("🚨 تراکنش‌های مشکوک")
        anomaly_layout = QVBoxLayout()
        
        suspicious_count = 0
        for t in self.db.get_all_transactions(50):
            if self.db.detect_anomaly(t):
                suspicious_count += 1
        
        anomaly_layout.addWidget(QLabel(f"تعداد تراکنش‌های مشکوک: {suspicious_count}"))
        
        if suspicious_count > 0:
            anomaly_layout.addWidget(QLabel("⚠️ برخی تراکنش‌ها نیاز به بررسی دارند"))
        else:
            anomaly_layout.addWidget(QLabel("✅ هیچ تراکنش مشکوکی یافت نشد"))
        
        anomaly_group.setLayout(anomaly_layout)
        layout.addWidget(anomaly_group)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


# ====================== کلاس TransactionDialog ======================

class TransactionDialog(QDialog):
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("➕ ثبت تراکنش جدید")
        self.setFixedSize(self.optimizer.get_size(550), self.optimizer.get_size(600))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['card_bg']};
                border: 2px solid {self.theme['primary']};
                border-radius: {self.optimizer.get_margin(15)}px;
            }}
            QLabel {{
                color: {self.theme['text']};
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
                padding: {self.optimizer.get_margin(10)}px;
                border: 2px solid {self.theme['border']};
                border-radius: {self.optimizer.get_margin(6)}px;
                background: {self.theme['background']};
                color: {self.theme['text']};
                font-size: {self.optimizer.get_font_size(11)}px;
                min-height: {self.optimizer.get_button_height(40)}px;
            }}
            QPushButton {{
                padding: {self.optimizer.get_margin(12)}px {self.optimizer.get_margin(24)}px;
                border: none;
                border-radius: {self.optimizer.get_margin(6)}px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(12)}px;
                min-height: {self.optimizer.get_button_height(45)}px;
            }}
            QPushButton#saveBtn {{
                background-color: {self.theme['success']};
                color: white;
            }}
            QPushButton#cancelBtn {{
                background-color: {self.theme['danger']};
                color: white;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing(20))
        layout.setContentsMargins(
            self.optimizer.get_margin(30),
            self.optimizer.get_margin(30),
            self.optimizer.get_margin(30),
            self.optimizer.get_margin(30)
        )
        
        form_layout = QFormLayout()
        form_layout.setSpacing(self.optimizer.get_spacing(15))
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedHeight(self.optimizer.get_button_height(45))
        form_layout.addRow("📅 تاریخ:", self.date_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(self.optimizer.get_button_height(100))
        self.desc_edit.setPlaceholderText("شرح تراکنش را وارد کنید...")
        form_layout.addRow("📝 شرح:", self.desc_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["درآمد", "هزینه", "انتقال"])
        self.type_combo.setFixedHeight(self.optimizer.get_button_height(45))
        form_layout.addRow("📊 نوع:", self.type_combo)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setPrefix("ریال ")
        self.amount_spin.setGroupSeparatorShown(True)
        self.amount_spin.setFixedHeight(self.optimizer.get_button_height(45))
        form_layout.addRow("💰 مبلغ:", self.amount_spin)
        
        self.debit_combo = QComboBox()
        self.debit_combo.setFixedHeight(self.optimizer.get_button_height(45))
        self.debit_combo.setMaxVisibleItems(15)
        form_layout.addRow("📤 حساب بدهکار:", self.debit_combo)
        
        self.credit_combo = QComboBox()
        self.credit_combo.setFixedHeight(self.optimizer.get_button_height(45))
        self.credit_combo.setMaxVisibleItems(15)
        form_layout.addRow("📥 حساب بستانکار:", self.credit_combo)
        
        layout.addLayout(form_layout)
        
        self.load_accounts()
        
        # هشدار هوش مصنوعی (اگه تراکنش مشکوک باشه)
        if self.amount_spin.value() > 0:
            warning_label = QLabel("")
            layout.addWidget(warning_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(self.optimizer.get_spacing(15))
        
        self.save_btn = QPushButton("💾 ذخیره تراکنش")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(self.optimizer.get_button_height(45))
        self.save_btn.clicked.connect(self.save_transaction)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✖ انصراف")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedHeight(self.optimizer.get_button_height(45))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        accounts = self.db.get_all_accounts()
        
        self.debit_combo.clear()
        self.credit_combo.clear()
        
        self.debit_combo.addItem("─── انتخاب کنید ───", None)
        self.credit_combo.addItem("─── انتخاب کنید ───", None)
        
        for acc in accounts:
            if acc.is_active:
                text = f"{acc.code} - {acc.name}"
                self.debit_combo.addItem(text, acc.id)
                self.credit_combo.addItem(text, acc.id)
        
        self.debit_combo.setCurrentIndex(0)
        self.credit_combo.setCurrentIndex(0)
    
    def save_transaction(self):
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "خطا", "مبلغ باید بزرگتر از صفر باشد")
            return
        
        if self.debit_combo.count() <= 1 or self.credit_combo.count() <= 1:
            QMessageBox.warning(self, "خطا", "هیچ حسابی برای انتخاب وجود ندارد")
            return
        
        debit_id = self.debit_combo.currentData()
        credit_id = self.credit_combo.currentData()
        
        if debit_id is None or credit_id is None:
            QMessageBox.warning(self, "خطا", "لطفاً حساب‌ها را انتخاب کنید")
            return
        
        if debit_id == credit_id:
            QMessageBox.warning(self, "خطا", "حساب‌ها نمی‌توانند یکسان باشند")
            return
        
        qdate = self.date_edit.date()
        date = datetime(qdate.year(), qdate.month(), qdate.day())
        
        transaction = Transaction(
            date=date,
            description=self.desc_edit.toPlainText(),
            amount=self.amount_spin.value(),
            type=self.type_combo.currentText(),
            debit_account_id=debit_id,
            credit_account_id=credit_id
        )
        
        # بررسی با هوش مصنوعی
        if self.db.detect_anomaly(transaction):
            reply = QMessageBox.question(
                self, 
                "⚠️ هشدار هوش مصنوعی",
                "این تراکنش مشکوک تشخیص داده شده!\nآیا مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        if self.db.add_transaction(transaction):
            QMessageBox.information(self, "موفق", "✅ تراکنش با موفقیت ثبت شد")
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", "❌ خطا در ثبت تراکنش")


# ====================== کلاس AccountsDialog ======================

class AccountsDialog(QDialog):
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("📊 لیست حساب‌ها")
        self.setFixedSize(self.optimizer.get_size(600), self.optimizer.get_size(400))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['background']};
            }}
            QTableWidget {{
                background-color: {self.theme['card_bg']};
                color: {self.theme['text']};
                alternate-background-color: {self.theme['secondary']};
                gridline-color: {self.theme['border']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QHeaderView::section {{
                background-color: {self.theme['secondary']};
                color: {self.theme['text']};
                padding: {self.optimizer.get_margin(5)}px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton {{
                background-color: {self.theme['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin(5)}px;
                padding: {self.optimizer.get_margin(10)}px {self.optimizer.get_margin(20)}px;
                font-size: {self.optimizer.get_font_size(11)}px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["کد", "نام", "نوع", "موجودی"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.load_accounts()
        
        layout.addWidget(self.table)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        accounts = self.db.get_all_accounts()
        self.table.setRowCount(len(accounts))
        
        type_map = {
            'asset': 'دارایی',
            'liability': 'بدهی',
            'equity': 'سرمایه',
            'revenue': 'درآمد',
            'expense': 'هزینه'
        }
        
        for i, acc in enumerate(accounts):
            self.table.setItem(i, 0, QTableWidgetItem(acc.code))
            self.table.setItem(i, 1, QTableWidgetItem(acc.name))
            self.table.setItem(i, 2, QTableWidgetItem(type_map.get(acc.type, acc.type)))
            
            balance = QTableWidgetItem(f"{acc.balance:,.0f}")
            balance.setTextAlignment(Qt.AlignRight)
            if acc.balance >= 0:
                balance.setForeground(QColor(self.theme['success']))
            else:
                balance.setForeground(QColor(self.theme['danger']))
            self.table.setItem(i, 3, balance)


# ====================== کلاس TransactionsDialog ======================

class TransactionsDialog(QDialog):
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("📋 لیست تراکنش‌ها")
        self.setFixedSize(self.optimizer.get_size(800), self.optimizer.get_size(500))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['background']};
            }}
            QTableWidget {{
                background-color: {self.theme['card_bg']};
                color: {self.theme['text']};
                alternate-background-color: {self.theme['secondary']};
                gridline-color: {self.theme['border']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QHeaderView::section {{
                background-color: {self.theme['secondary']};
                color: {self.theme['text']};
                padding: {self.optimizer.get_margin(5)}px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton {{
                background-color: {self.theme['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin(5)}px;
                padding: {self.optimizer.get_margin(10)}px {self.optimizer.get_margin(20)}px;
                font-size: {self.optimizer.get_font_size(11)}px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["شماره", "تاریخ", "شرح", "نوع", "مبلغ", "وضعیت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.load_transactions()
        
        layout.addWidget(self.table)
        
        # دکمه تحلیل هوشمند
        ai_btn = QPushButton("🤖 تحلیل هوشمند تراکنش‌ها")
        ai_btn.clicked.connect(self.show_ai_analysis)
        layout.addWidget(ai_btn)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_transactions(self):
        transactions = self.db.get_all_transactions(50)
        self.table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            self.table.setItem(i, 0, QTableWidgetItem(trans.number))
            self.table.setItem(i, 1, QTableWidgetItem(trans.date.strftime("%Y/%m/%d")))
            self.table.setItem(i, 2, QTableWidgetItem(trans.description[:30]))
            self.table.setItem(i, 3, QTableWidgetItem(trans.type))
            
            amount = QTableWidgetItem(f"{trans.amount:,.0f}")
            amount.setTextAlignment(Qt.AlignRight)
            
            # رنگ‌بندی با هوش مصنوعی
            if self.db.detect_anomaly(trans):
                amount.setForeground(QColor(self.theme['danger']))
                amount.setToolTip("⚠️ تراکنش مشکوک")
            elif trans.type == "درآمد":
                amount.setForeground(QColor(self.theme['success']))
            else:
                amount.setForeground(QColor(self.theme['warning']))
            
            self.table.setItem(i, 4, amount)
            
            status = QTableWidgetItem("✅ تأیید")
            status.setForeground(QColor(self.theme['success']))
            self.table.setItem(i, 5, status)
    
    def show_ai_analysis(self):
        dialog = AIDashboard(self.db, self.optimizer, self.theme, self)
        dialog.exec_()


# ====================== کلاس LicenseDialog ======================

class LicenseDialog(QDialog):
    def __init__(self, license_manager: LicenseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("🔑 فعال‌سازی لایسنس")
        self.setFixedSize(self.optimizer.get_size(500), self.optimizer.get_size(400))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['card_bg']};
                border: 2px solid {self.theme['primary']};
                border-radius: {self.optimizer.get_margin(15)}px;
            }}
            QLabel {{
                color: {self.theme['text']};
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QTextEdit {{
                border: 2px solid {self.theme['border']};
                border-radius: {self.optimizer.get_margin(6)}px;
                padding: {self.optimizer.get_margin(8)}px;
                background: {self.theme['background']};
                color: {self.theme['text']};
                font-family: monospace;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton {{
                background-color: {self.theme['success']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin(6)}px;
                padding: {self.optimizer.get_margin(10)}px {self.optimizer.get_margin(20)}px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(11)}px;
                min-height: {self.optimizer.get_button_height(40)}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['hover']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing(20))
        
        title = QLabel("🔑 فعال‌سازی لایسنس")
        title.setStyleSheet(f"font-size: {self.optimizer.get_font_size(18)}px; font-weight: bold; color: {self.theme['primary']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        hwid_label = QLabel(f"شناسه سیستم:")
        layout.addWidget(hwid_label)
        
        hwid_value = QLabel(self.license.hardware_id)
        hwid_value.setStyleSheet(f"""
            font-family: monospace;
            background: {self.theme['background']};
            color: {self.theme['text']};
            padding: {self.optimizer.get_margin(10)}px;
            border-radius: {self.optimizer.get_margin(5)}px;
            border: 1px solid {self.theme['border']};
        """)
        hwid_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        hwid_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(hwid_value)
        
        status_label = QLabel(f"وضعیت فعلی: {self.license.license_type.value}")
        layout.addWidget(status_label)
        
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("کلید لایسنس را وارد کنید...")
        self.key_input.setMaximumHeight(self.optimizer.get_button_height(100))
        layout.addWidget(self.key_input)
        
        activate_btn = QPushButton("✅ فعال‌سازی")
        activate_btn.clicked.connect(self.activate)
        layout.addWidget(activate_btn)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def activate(self):
        key = self.key_input.toPlainText().strip()
        if not key:
            QMessageBox.warning(self, "خطا", "کلید لایسنس را وارد کنید")
            return
        
        valid, msg, ltype = self.license.validate_license(key)
        if valid:
            self.license.save_license(key, ltype)
            QMessageBox.information(self, "موفق", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", msg)


# ====================== کلاس AboutDialog ======================

class AboutDialog(QDialog):
    def __init__(self, license_manager: LicenseManager, optimizer: ScreenOptimizer, theme: dict, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = optimizer
        self.theme = theme
        
        self.setWindowTitle("ℹ️ درباره ایمان حسابداری")
        self.setFixedSize(self.optimizer.get_size(500), self.optimizer.get_size(450))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['card_bg']};
                border: 2px solid {self.theme['primary']};
                border-radius: {self.optimizer.get_margin(15)}px;
            }}
            QLabel {{
                color: {self.theme['text']};
            }}
            QPushButton {{
                background-color: {self.theme['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin(6)}px;
                padding: {self.optimizer.get_margin(10)}px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout()
        
        logo = QLabel("⚡💰")
        logo.setStyleSheet(f"font-size: {self.optimizer.get_icon_size(60)}px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size: {self.optimizer.get_font_size(22)}px; font-weight: bold; color: {self.theme['primary']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f"نسخه {APP_VERSION} (با ImanAILight داخلی)")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        slogan = QLabel(APP_SLOGAN)
        slogan.setStyleSheet(f"color: {self.theme['success']}; font-style: italic;")
        slogan.setAlignment(Qt.AlignCenter)
        layout.addWidget(slogan)
        
        author = QLabel(f"توسعه‌دهنده: {APP_AUTHOR}")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)
        
        contact = QLabel(f"📧 {APP_EMAIL}\n🌐 {APP_WEBSITE}\n📱 {APP_TELEGRAM}")
        contact.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact)
        
        if self.license.is_school:
            license_text = "🏫 نسخه ویژه مدرسه"
        elif self.license.is_admin:
            license_text = "👑 دسترسی ادمین"
        else:
            license_text = f"🔑 {self.license.license_type.value}"
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet(f"color: {self.theme['success']}; font-weight: bold;")
        license_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_label)
        
        ai_label = QLabel("🤖 مجهز به ImanAILight - هوش مصنوعی اختصاصی")
        ai_label.setStyleSheet(f"color: {self.theme['primary']};")
        ai_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ai_label)
        
        layout.addStretch()
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


# ====================== کلاس DashboardWidget ======================

class DashboardWidget(QWidget):
    def __init__(self, db: DatabaseManager, license_mgr: LicenseManager, theme_manager: ThemeManager):
        super().__init__()
        self.db = db
        self.license = license_mgr
        self.theme_manager = theme_manager
        self.optimizer = theme_manager.optimizer
        self.theme = theme_manager.current_theme
        
        self.setStyleSheet(f"background-color: {self.theme['background']};")
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing(15))
        
        # وضعیت لایسنس
        license_frame = QFrame()
        license_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.theme['card_bg']};
                border-radius: {self.optimizer.get_margin(10)}px;
                border: 1px solid {self.theme['border']};
                padding: {self.optimizer.get_margin(10)}px;
            }}
        """)
        license_layout = QHBoxLayout()
        
        if self.license.is_school:
            license_text = "🏫 نسخه مدرسه"
            color = self.theme['success']
        elif self.license.is_admin:
            license_text = "👑 ادمین"
            color = self.theme['warning']
        else:
            license_text = f"🔑 {self.license.license_type.value}"
            color = self.theme['text_secondary']
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: {self.optimizer.get_font_size(14)}px;")
        license_layout.addWidget(license_label)
        license_layout.addStretch()
        license_frame.setLayout(license_layout)
        layout.addWidget(license_frame)
        
        # کارت‌های آماری
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(self.optimizer.get_spacing(15))
        
        self.total_card = StatCard(
            "موجودی کل", "۰", "💰", 
            self.theme['primary'], self.optimizer, self.theme
        )
        stats_layout.addWidget(self.total_card)
        
        self.income_card = StatCard(
            "درآمد امروز", "۰", "📈", 
            self.theme['success'], self.optimizer, self.theme
        )
        stats_layout.addWidget(self.income_card)
        
        self.expense_card = StatCard(
            "هزینه امروز", "۰", "📉", 
            self.theme['danger'], self.optimizer, self.theme
        )
        stats_layout.addWidget(self.expense_card)
        
        layout.addLayout(stats_layout)
        
        # دکمه‌ها
        btn_layout = QGridLayout()
        btn_layout.setSpacing(self.optimizer.get_spacing(10))
        
        buttons = [
            ("➕ تراکنش جدید", self.show_transaction, 0, 0, self.theme['success']),
            ("📊 لیست حساب‌ها", self.show_accounts, 0, 1, self.theme['info']),
            ("📋 لیست تراکنش‌ها", self.show_transactions, 1, 0, self.theme['warning']),
            ("🤖 هوش مصنوعی", self.show_ai, 1, 1, self.theme['primary']),
            ("🔑 لایسنس", self.show_license, 2, 0, self.theme['secondary']),
            ("ℹ️ درباره", self.show_about, 2, 1, self.theme['secondary'])
        ]
        
        for text, func, row, col, color in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(self.optimizer.get_button_height(40))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: {self.optimizer.get_margin(6)}px;
                    padding: {self.optimizer.get_margin(8)}px;
                    font-size: {self.optimizer.get_font_size(11)}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.theme['hover']};
                }}
            """)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn, row, col)
        
        layout.addLayout(btn_layout)
        
        # هشدار هوش مصنوعی
        expenses = [t.amount for t in self.db.get_all_transactions() if t.type == "هزینه"]
        if expenses and len(expenses) > 5:
            pred = self.db.predict_next_expense()
            trend = self.db.trend_analysis()
            
            ai_frame = QFrame()
            ai_frame.setStyleSheet(f"""
                QFrame {{
                    background: {self.theme['card_bg']};
                    border-radius: {self.optimizer.get_margin(8)}px;
                    border: 1px solid {self.theme['primary']};
                    padding: {self.optimizer.get_margin(8)}px;
                }}
            """)
            ai_layout = QHBoxLayout()
            
            ai_icon = QLabel("🤖")
            ai_icon.setStyleSheet(f"font-size: {self.optimizer.get_font_size(20)}px;")
            ai_layout.addWidget(ai_icon)
            
            ai_text = QLabel(f"پیش‌بینی ماه آینده: {pred:,.0f} ({trend})")
            ai_text.setStyleSheet(f"color: {self.theme['primary']}; font-weight: bold;")
            ai_layout.addWidget(ai_text)
            
            ai_layout.addStretch()
            ai_frame.setLayout(ai_layout)
            layout.addWidget(ai_frame)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh(self):
        total = self.db.get_total_balance()
        self.total_card.update_value(f"{total:,.0f}")
        
        income, expense = self.db.get_today_income_expense()
        self.income_card.update_value(f"{income:,.0f}")
        self.expense_card.update_value(f"{expense:,.0f}")
    
    def show_transaction(self):
        dialog = TransactionDialog(self.db, self.optimizer, self.theme, self.window())
        if dialog.exec_():
            self.refresh()
    
    def show_accounts(self):
        dialog = AccountsDialog(self.db, self.optimizer, self.theme, self.window())
        dialog.exec_()
    
    def show_transactions(self):
        dialog = TransactionsDialog(self.db, self.optimizer, self.theme, self.window())
        dialog.exec_()
    
    def show_ai(self):
        dialog = AIDashboard(self.db, self.optimizer, self.theme, self.window())
        dialog.exec_()
    
    def show_license(self):
        dialog = LicenseDialog(self.license, self.optimizer, self.theme, self.window())
        if dialog.exec_():
            QMessageBox.information(self.window(), "موفق", "لایسنس فعال شد")
    
    def show_about(self):
        dialog = AboutDialog(self.license, self.optimizer, self.theme, self.window())
        dialog.exec_()


# ====================== کلاس MainWindow ======================

class MainWindow(QMainWindow):
    def __init__(self, db, license_mgr):
        super().__init__()
        self.db = db
        self.license = license_mgr
        self.optimizer = ScreenOptimizer()
        self.theme_manager = ThemeManager(self.optimizer)
        
        w = self.optimizer.get_size(1200)
        h = self.optimizer.get_size(700)
        self.resize(w, h)
        
        title = APP_NAME
        if self.license.is_school:
            title += " [نسخه مدرسه]"
        elif self.license.is_admin:
            title += " [ادمین]"
        
        self.setWindowTitle(title)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        self.apply_theme()
        
        self.init_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
    
    def apply_theme(self):
        self.setStyleSheet(self.theme_manager.get_style())
    
    def change_theme(self, theme_name):
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()
        
        if hasattr(self, 'dashboard'):
            self.dashboard.theme = self.theme_manager.current_theme
            self.dashboard.setStyleSheet(f"background-color: {self.theme_manager.current_theme['background']};")
    
    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        self.dashboard = DashboardWidget(self.db, self.license, self.theme_manager)
        self.tabs.addTab(self.dashboard, "🏠 داشبورد")
        
        self.tabs.addTab(QWidget(), "📊 گزارشات")
        self.tabs.addTab(QWidget(), "⚙️ تنظیمات")
        
        self.setCentralWidget(self.tabs)
    
    def create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("فایل")
        
        license_action = QAction("🔑 فعال‌سازی لایسنس", self)
        license_action.triggered.connect(self.dashboard.show_license)
        file_menu.addAction(license_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        settings_menu = menubar.addMenu("⚙️ تنظیمات")
        
        theme_menu = settings_menu.addMenu("🎨 تم برنامه")
        
        dark_action = QAction("🌙 تم تیره", self)
        dark_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("☀️ تم روشن", self)
        light_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_action)
        
        ai_menu = menubar.addMenu("🤖 هوش مصنوعی")
        
        predict_action = QAction("📊 پیش‌بینی هزینه", self)
        predict_action.triggered.connect(self.dashboard.show_ai)
        ai_menu.addAction(predict_action)
        
        help_menu = menubar.addMenu("راهنما")
        
        about_action = QAction("ℹ️ درباره", self)
        about_action.triggered.connect(self.dashboard.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = self.addToolBar("ابزارها")
        toolbar.setMovable(False)
        
        icon_size = self.optimizer.get_icon_size(24)
        toolbar.setIconSize(QSize(icon_size, icon_size))
        
        trans_btn = QAction("➕", self)
        trans_btn.setToolTip("تراکنش جدید")
        trans_btn.triggered.connect(self.dashboard.show_transaction)
        toolbar.addAction(trans_btn)
        
        accounts_btn = QAction("📊", self)
        accounts_btn.setToolTip("لیست حساب‌ها")
        accounts_btn.triggered.connect(self.dashboard.show_accounts)
        toolbar.addAction(accounts_btn)
        
        transactions_btn = QAction("📋", self)
        transactions_btn.setToolTip("لیست تراکنش‌ها")
        transactions_btn.triggered.connect(self.dashboard.show_transactions)
        toolbar.addAction(transactions_btn)
        
        ai_btn = QAction("🤖", self)
        ai_btn.setToolTip("هوش مصنوعی")
        ai_btn.triggered.connect(self.dashboard.show_ai)
        toolbar.addAction(ai_btn)
        
        toolbar.addSeparator()
    
    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        theme = self.theme_manager.current_theme
        
        if self.license.is_school:
            status = "🏫 نسخه مدرسه"
            color = theme['success']
        elif self.license.is_admin:
            status = "👑 ادمین"
            color = theme['warning']
        else:
            status = f"🔑 {self.license.license_type.value}"
            color = theme['text_light']
        
        label = QLabel(status)
        label.setStyleSheet(f"color: {color};")
        self.statusbar.addPermanentWidget(label)
        
        ai_label = QLabel("🤖 ImanAILight فعال")
        ai_label.setStyleSheet(f"color: {theme['primary']};")
        self.statusbar.addPermanentWidget(ai_label)
        
        self.date_label = QLabel()
        self.statusbar.addPermanentWidget(self.date_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
        
        self.update_status()
    
    def update_status(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("yyyy/MM/dd HH:mm"))


# ====================== تابع اصلی ======================

def main():
    app = QApplication(sys.argv)
    
    db = DatabaseManager()
    license_mgr = LicenseManager()
    
    if license_mgr.license_type == LicenseType.FREE and not license_mgr.is_school:
        optimizer = ScreenOptimizer()
        theme = THEMES["dark"]
        dialog = LicenseDialog(license_mgr, optimizer, theme)
        dialog.exec_()
    
    window = MainWindow(db, license_mgr)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
