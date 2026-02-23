#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ایمان حسابداری - ImanAccounting
نسخه ۷.۴.۰ - نسخه نهایی با همه قابلیت‌ها
ایمان جان - ۱۴۰۳
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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# ====================== اطلاعات برند ======================

APP_NAME = "ایمان حسابداری"
APP_NAME_EN = "ImanAccounting"
APP_VERSION = "7.4.0"
APP_AUTHOR = "ایمان"
APP_SLOGAN = "حساب‌هایت رو به ایمان بسپار"
APP_WEBSITE = "iman-accounting.ir"
APP_EMAIL = "neonpresents01@gmail.com"
APP_TELEGRAM = "@ImanAccounting"

ADMIN_SECRET_KEY = "Iman@Admin@2024#SuperSecret"

COLORS = {
    'primary': '#3498db',
    'secondary': '#2c3e50',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#2980b9',
    'light': '#ecf0f1',
    'dark': '#34495e',
    'white': '#ffffff',
    'black': '#000000',
    'background': '#f5f6fa',
    'card_bg': '#ffffff',
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
    'text_light': '#ecf0f1',
    'border': '#dcdde1'
}


# ====================== مدل‌های داده ======================

class Account:
    """مدل حساب"""
    def __init__(self, code: str, name: str, type: str, parent_id: int = None):
        self.id = None
        self.code = code
        self.name = name
        self.type = type
        self.parent_id = parent_id
        self.balance = 0.0
        self.is_active = True
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'balance': self.balance
        }


class Transaction:
    """مدل تراکنش"""
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
    
    def to_dict(self) -> dict:
        return {
            'number': self.number,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'amount': self.amount,
            'type': self.type
        }


# ====================== سیستم پلاگین ======================

class PluginSignature:
    """مدیریت امضای پلاگین‌ها"""
    SIGNATURE = "IMAN_ACCOUNTING_PLUGIN_2024"
    
    @classmethod
    def verify_file(cls, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)
            
            if f'PLUGIN_SIGNATURE = "{cls.SIGNATURE}"' in content:
                return True
            if f"PLUGIN_SIGNATURE = '{cls.SIGNATURE}'" in content:
                return True
            return False
        except:
            return False


class PluginBase:
    """کلاس پایه برای پلاگین‌ها"""
    def __init__(self):
        self.core = None
        self.name = ""
        self.version = ""
        self.author = ""
    
    def get_info(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author
        }
    
    def on_load(self, core_proxy):
        self.core = core_proxy
        return True
    
    def get_menu_items(self) -> list:
        return []
    
    def get_toolbar_items(self) -> list:
        return []
    
    def get_dashboard_widgets(self):
        return []


class PluginLoader:
    """بارگذاری‌کننده پلاگین‌ها"""
    
    def __init__(self, core):
        self.core = core
        self.plugins = []
        self.plugin_folder = "plugins"
        self.create_folder()
    
    def create_folder(self):
        if not os.path.exists(self.plugin_folder):
            os.makedirs(self.plugin_folder)
        
        init_file = os.path.join(self.plugin_folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# پکیج پلاگین‌ها\n")
    
    def discover_plugins(self):
        """کشف و بارگذاری پلاگین‌ها"""
        print("🔍 در حال جستجوی پلاگین‌ها...")
        count = 0
        
        if not os.path.exists(self.plugin_folder):
            return 0
        
        for file in os.listdir(self.plugin_folder):
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(self.plugin_folder, file)
                if self.load_plugin(file_path):
                    count += 1
        
        print(f"✅ {count} پلاگین بارگذاری شد")
        return count
    
    def load_plugin(self, file_path: str) -> bool:
        try:
            module_name = os.path.basename(file_path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # پیدا کردن کلاس پلاگین
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'get_info'):
                    plugin_instance = obj()
                    info = plugin_instance.get_info()
                    
                    self.plugins.append({
                        'instance': plugin_instance,
                        'info': info,
                        'file': file_path
                    })
                    
                    print(f"✅ پلاگین {info.get('name', name)} بارگذاری شد")
                    return True
            
            return False
        except Exception as e:
            print(f"❌ خطا در بارگذاری {file_path}: {e}")
            return False
    
    def get_all_plugins(self):
        return self.plugins


# ====================== بهینه‌ساز صفحه نمایش ======================

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


# ====================== سیستم لایسنس ======================

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
            'school': 'دبیرستان'
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


# ====================== دیتابیس ======================

class DatabaseManager:
    """مدیریت پایگاه داده"""
    
    def __init__(self, db_path: str = "iman_accounting.db"):
        self.db_path = db_path
        self.accounts = []
        self.transactions = []
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugins (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    author TEXT,
                    filename TEXT,
                    enabled INTEGER DEFAULT 1,
                    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


# ====================== دیالوگ ثبت تراکنش ======================

class TransactionDialog(QDialog):
    """دیالوگ ثبت تراکنش جدید"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("➕ ثبت تراکنش جدید")
        self.setFixedSize(self.optimizer.get_size(550), self.optimizer.get_size(600))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
                padding: 10px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                background: white;
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(11)}px;
                min-height: 40px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                selection-color: white;
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QPushButton {{
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(12)}px;
                min-height: 45px;
            }}
            QPushButton#saveBtn {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton#saveBtn:hover {{
                background-color: #229954;
            }}
            QPushButton#cancelBtn {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # تاریخ
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedHeight(45)
        form_layout.addRow("📅 تاریخ:", self.date_edit)
        
        # شرح
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("شرح تراکنش را وارد کنید...")
        form_layout.addRow("📝 شرح:", self.desc_edit)
        
        # نوع
        self.type_combo = QComboBox()
        self.type_combo.addItems(["درآمد", "هزینه", "انتقال"])
        self.type_combo.setFixedHeight(45)
        form_layout.addRow("📊 نوع:", self.type_combo)
        
        # مبلغ
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setPrefix("ریال ")
        self.amount_spin.setGroupSeparatorShown(True)
        self.amount_spin.setFixedHeight(45)
        form_layout.addRow("💰 مبلغ:", self.amount_spin)
        
        # حساب بدهکار
        self.debit_combo = QComboBox()
        self.debit_combo.setFixedHeight(45)
        self.debit_combo.setMaxVisibleItems(15)
        form_layout.addRow("📤 حساب بدهکار:", self.debit_combo)
        
        # حساب بستانکار
        self.credit_combo = QComboBox()
        self.credit_combo.setFixedHeight(45)
        self.credit_combo.setMaxVisibleItems(15)
        form_layout.addRow("📥 حساب بستانکار:", self.credit_combo)
        
        layout.addLayout(form_layout)
        
        self.load_accounts()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.save_btn = QPushButton("💾 ذخیره تراکنش")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(45)
        self.save_btn.clicked.connect(self.save_transaction)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✖ انصراف")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        btn_layout.addStretch()
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
        
        if self.db.add_transaction(transaction):
            QMessageBox.information(self, "موفق", "✅ تراکنش با موفقیت ثبت شد")
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", "❌ خطا در ثبت تراکنش")


# ====================== دیالوگ لیست حساب‌ها ======================

class AccountsDialog(QDialog):
    """دیالوگ نمایش لیست حساب‌ها"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("📊 لیست حساب‌ها")
        self.setFixedSize(self.optimizer.get_size(600), self.optimizer.get_size(400))
        
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
        
        for i, acc in enumerate(accounts):
            self.table.setItem(i, 0, QTableWidgetItem(acc.code))
            self.table.setItem(i, 1, QTableWidgetItem(acc.name))
            self.table.setItem(i, 2, QTableWidgetItem(acc.type))
            
            balance = QTableWidgetItem(f"{acc.balance:,.0f}")
            balance.setTextAlignment(Qt.AlignRight)
            self.table.setItem(i, 3, balance)


# ====================== دیالوگ لیست تراکنش‌ها ======================

class TransactionsDialog(QDialog):
    """دیالوگ نمایش لیست تراکنش‌ها"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("📋 لیست تراکنش‌ها")
        self.setFixedSize(self.optimizer.get_size(800), self.optimizer.get_size(500))
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["شماره", "تاریخ", "شرح", "نوع", "مبلغ", "وضعیت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.load_transactions()
        
        layout.addWidget(self.table)
        
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
            self.table.setItem(i, 4, amount)
            
            status = QTableWidgetItem("✅ تأیید")
            status.setForeground(QColor(COLORS['success']))
            self.table.setItem(i, 5, status)


# ====================== دیالوگ مدیریت پلاگین ======================

class PluginManagerDialog(QDialog):
    """دیالوگ مدیریت پلاگین‌ها"""
    
    def __init__(self, plugin_loader: PluginLoader, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.plugin_loader = plugin_loader
        self.optimizer = optimizer
        
        self.setWindowTitle("📦 مدیریت پلاگین‌ها")
        self.setFixedSize(self.optimizer.get_size(600), self.optimizer.get_size(400))
        
        layout = QVBoxLayout()
        
        # لیست پلاگین‌ها
        self.list_widget = QListWidget()
        
        for plugin in self.plugin_loader.get_all_plugins():
            info = plugin['info']
            item_text = f"✅ {info.get('name', 'ناشناس')} v{info.get('version', '1.0')} - {info.get('author', 'ناشناس')}"
            self.list_widget.addItem(item_text)
        
        if self.list_widget.count() == 0:
            self.list_widget.addItem("ℹ️ هیچ پلاگینی نصب نشده است")
        
        layout.addWidget(QLabel("پلاگین‌های نصب شده:"))
        layout.addWidget(self.list_widget)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def refresh(self):
        self.plugin_loader.discover_plugins()
        self.list_widget.clear()
        
        for plugin in self.plugin_loader.get_all_plugins():
            info = plugin['info']
            item_text = f"✅ {info.get('name', 'ناشناس')} v{info.get('version', '1.0')}"
            self.list_widget.addItem(item_text)
        
        if self.list_widget.count() == 0:
            self.list_widget.addItem("ℹ️ هیچ پلاگینی نصب نشده است")


# ====================== دیالوگ لایسنس ======================

class LicenseDialog(QDialog):
    """دیالوگ فعال‌سازی لایسنس"""
    
    def __init__(self, license_manager: LicenseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = optimizer
        
        self.setWindowTitle("🔑 فعال‌سازی لایسنس")
        self.setFixedSize(self.optimizer.get_size(500), self.optimizer.get_size(400))
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # عنوان
        title = QLabel("فعال‌سازی لایسنس")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # HWID
        hwid_label = QLabel(f"شناسه سیستم:")
        layout.addWidget(hwid_label)
        
        hwid_value = QLabel(self.license.hardware_id)
        hwid_value.setStyleSheet("font-family: monospace; background: #ecf0f1; padding: 10px; border-radius: 5px;")
        hwid_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        hwid_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(hwid_value)
        
        # وضعیت فعلی
        status_label = QLabel(f"وضعیت فعلی: {self.license.license_type.value}")
        layout.addWidget(status_label)
        
        # ورود لایسنس
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("کلید لایسنس را وارد کنید...")
        self.key_input.setMaximumHeight(100)
        layout.addWidget(self.key_input)
        
        # دکمه فعال‌سازی
        activate_btn = QPushButton("✅ فعال‌سازی")
        activate_btn.clicked.connect(self.activate)
        layout.addWidget(activate_btn)
        
        # دکمه بستن
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


# ====================== دیالوگ درباره ======================

class AboutDialog(QDialog):
    """دیالوگ درباره برنامه"""
    
    def __init__(self, license_manager: LicenseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = optimizer
        
        self.setWindowTitle("ℹ️ درباره ایمان حسابداری")
        self.setFixedSize(self.optimizer.get_size(500), self.optimizer.get_size(400))
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # لوگو
        logo = QLabel("⚡💰")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # عنوان
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # نسخه
        version = QLabel(f"نسخه {APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # شعار
        slogan = QLabel(APP_SLOGAN)
        slogan.setStyleSheet("color: #27ae60; font-style: italic;")
        slogan.setAlignment(Qt.AlignCenter)
        layout.addWidget(slogan)
        
        # اطلاعات تماس
        contact = QLabel(f"📧 {APP_EMAIL}\n🌐 {APP_WEBSITE}\n📱 {APP_TELEGRAM}")
        contact.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact)
        
        # وضعیت لایسنس
        if self.license.is_school:
            license_text = "🏫 نسخه ویژه مدرسه"
        elif self.license.is_admin:
            license_text = "👑 دسترسی ادمین"
        else:
            license_text = f"🔑 {self.license.license_type.value}"
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        license_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_label)
        
        layout.addStretch()
        
        # دکمه بستن
        close_btn = QPushButton("✖ بستن")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


# ====================== کارت آماری ======================

class StatCard(QFrame):
    """کارت آمار"""
    
    def __init__(self, title: str, value: str, icon: str, color: str):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 30px; background: transparent; color: white;")
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8);")
        text_layout.addWidget(title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        text_layout.addWidget(self.value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_value(self, value):
        self.value_label.setText(value)


# ====================== داشبورد ======================

class DashboardWidget(QWidget):
    """داشبورد اصلی"""
    
    def __init__(self, core, db, license_mgr, plugin_loader):
        super().__init__()
        self.core = core
        self.db = db
        self.license = license_mgr
        self.plugin_loader = plugin_loader
        self.optimizer = ScreenOptimizer()
        
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_size(15))
        layout.setContentsMargins(20, 20, 20, 20)
        
        # وضعیت لایسنس
        license_frame = QFrame()
        license_frame.setStyleSheet(f"background: white; border-radius: 10px; padding: 10px;")
        license_layout = QHBoxLayout()
        
        if self.license.is_school:
            license_text = "🏫 نسخه مدرسه"
            color = COLORS['success']
        elif self.license.is_admin:
            license_text = "👑 ادمین"
            color = COLORS['warning']
        else:
            license_text = f"🔑 {self.license.license_type.value}"
            color = COLORS['text_secondary']
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        license_layout.addWidget(license_label)
        license_layout.addStretch()
        license_frame.setLayout(license_layout)
        layout.addWidget(license_frame)
        
        # کارت‌های آماری
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(self.optimizer.get_size(15))
        
        self.total_card = StatCard("موجودی کل", "۰", "💰", COLORS['secondary'])
        stats_layout.addWidget(self.total_card)
        
        self.income_card = StatCard("درآمد امروز", "۰", "📈", COLORS['success'])
        stats_layout.addWidget(self.income_card)
        
        self.expense_card = StatCard("هزینه امروز", "۰", "📉", COLORS['danger'])
        stats_layout.addWidget(self.expense_card)
        
        layout.addLayout(stats_layout)
        
        # دکمه‌های سریع
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(self.optimizer.get_size(10))
        
        trans_btn = QPushButton("➕ تراکنش جدید")
        trans_btn.setFixedHeight(self.optimizer.get_size(40))
        trans_btn.clicked.connect(self.show_transaction)
        btn_layout.addWidget(trans_btn)
        
        accounts_btn = QPushButton("📊 لیست حساب‌ها")
        accounts_btn.setFixedHeight(self.optimizer.get_size(40))
        accounts_btn.clicked.connect(self.show_accounts)
        btn_layout.addWidget(accounts_btn)
        
        transactions_btn = QPushButton("📋 لیست تراکنش‌ها")
        transactions_btn.setFixedHeight(self.optimizer.get_size(40))
        transactions_btn.clicked.connect(self.show_transactions)
        btn_layout.addWidget(transactions_btn)
        
        plugins_btn = QPushButton("📦 مدیریت پلاگین‌ها")
        plugins_btn.setFixedHeight(self.optimizer.get_size(40))
        plugins_btn.clicked.connect(self.show_plugins)
        btn_layout.addWidget(plugins_btn)
        
        layout.addLayout(btn_layout)
        
        # منطقه ویجت‌های پلاگین
        self.plugin_area = QVBoxLayout()
        layout.addLayout(self.plugin_area)
        
        # اعمال ویجت‌های پلاگین
        self.apply_plugin_widgets()
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh(self):
        total = self.db.get_total_balance()
        self.total_card.update_value(f"{total:,.0f}")
        
        income, expense = self.db.get_today_income_expense()
        self.income_card.update_value(f"{income:,.0f}")
        self.expense_card.update_value(f"{expense:,.0f}")
    
    def show_transaction(self):
        dialog = TransactionDialog(self.db, self.optimizer, self.window())
        if dialog.exec_():
            self.refresh()
    
    def show_accounts(self):
        dialog = AccountsDialog(self.db, self.optimizer, self.window())
        dialog.exec_()
    
    def show_transactions(self):
        dialog = TransactionsDialog(self.db, self.optimizer, self.window())
        dialog.exec_()
    
    def show_plugins(self):
        dialog = PluginManagerDialog(self.plugin_loader, self.optimizer, self.window())
        dialog.exec_()
    
    def apply_plugin_widgets(self):
        """اعمال ویجت‌های پلاگین"""
        for plugin_data in self.plugin_loader.get_all_plugins():
            plugin = plugin_data['instance']
            if hasattr(plugin, 'get_dashboard_widgets'):
                widgets = plugin.get_dashboard_widgets()
                for widget_info in widgets:
                    try:
                        if callable(widget_info):
                            widget = widget_info(self)
                            self.plugin_area.addWidget(widget)
                    except:
                        pass


# ====================== پنجره اصلی ======================

class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    def __init__(self, core, db, license_mgr, plugin_loader):
        super().__init__()
        self.core = core
        self.db = db
        self.license = license_mgr
        self.plugin_loader = plugin_loader
        self.optimizer = ScreenOptimizer()
        
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
        
        self.init_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
    
    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        self.dashboard = DashboardWidget(self.core, self.db, self.license, self.plugin_loader)
        self.tabs.addTab(self.dashboard, "🏠 داشبورد")
        
        self.tabs.addTab(QWidget(), "📊 گزارشات")
        self.tabs.addTab(QWidget(), "⚙️ تنظیمات")
        
        self.setCentralWidget(self.tabs)
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("فایل")
        
        license_action = QAction("🔑 فعال‌سازی لایسنس", self)
        license_action.triggered.connect(self.show_license)
        file_menu.addAction(license_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # منوی پلاگین
        plugin_menu = menubar.addMenu("📦 پلاگین")
        
        for plugin_data in self.plugin_loader.get_all_plugins():
            plugin = plugin_data['instance']
            if hasattr(plugin, 'get_menu_items'):
                items = plugin.get_menu_items()
                for item in items:
                    action = QAction(item['title'], self)
                    action.triggered.connect(item['callback'])
                    plugin_menu.addAction(action)
        
        plugin_menu.addSeparator()
        
        manage_action = QAction("📋 مدیریت پلاگین‌ها", self)
        manage_action.triggered.connect(self.show_plugins)
        plugin_menu.addAction(manage_action)
        
        # منوی راهنما
        help_menu = menubar.addMenu("راهنما")
        
        about_action = QAction("ℹ️ درباره", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = self.addToolBar("ابزارها")
        toolbar.setMovable(False)
        
        icon_size = self.optimizer.get_size(24)
        toolbar.setIconSize(QSize(icon_size, icon_size))
        
        # دکمه‌های پیش‌فرض
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
        
        toolbar.addSeparator()
        
        # دکمه‌های پلاگین
        for plugin_data in self.plugin_loader.get_all_plugins():
            plugin = plugin_data['instance']
            if hasattr(plugin, 'get_toolbar_items'):
                items = plugin.get_toolbar_items()
                for item in items:
                    action = QAction(item['title'], self)
                    action.triggered.connect(item['callback'])
                    toolbar.addAction(action)
    
    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        if self.license.is_school:
            status = "🏫 نسخه مدرسه"
            color = COLORS['success']
        elif self.license.is_admin:
            status = "👑 ادمین"
            color = COLORS['warning']
        else:
            status = f"🔑 {self.license.license_type.value}"
            color = COLORS['text_light']
        
        label = QLabel(status)
        label.setStyleSheet(f"color: {color};")
        self.statusbar.addPermanentWidget(label)
        
        plugin_count = len(self.plugin_loader.get_all_plugins())
        plugin_label = QLabel(f"📦 {plugin_count} پلاگین")
        self.statusbar.addPermanentWidget(plugin_label)
        
        self.date_label = QLabel()
        self.statusbar.addPermanentWidget(self.date_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
        
        self.update_status()
    
    def update_status(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("yyyy/MM/dd HH:mm"))
    
    def show_license(self):
        dialog = LicenseDialog(self.license, self.optimizer, self)
        if dialog.exec_():
            QMessageBox.information(self, "موفق", "لایسنس فعال شد")
    
    def show_plugins(self):
        dialog = PluginManagerDialog(self.plugin_loader, self.optimizer, self)
        dialog.exec_()
    
    def show_about(self):
        dialog = AboutDialog(self.license, self.optimizer, self)
        dialog.exec_()


# ====================== کلاس Core ======================

class Core:
    """هسته اصلی برنامه"""
    
    def __init__(self):
        self.database = DatabaseManager()
        self.license = LicenseManager()
        self.plugin_loader = PluginLoader(self)
        self.current_user = {"name": "کاربر"}


# ====================== تابع اصلی ======================

def main():
    app = QApplication(sys.argv)
    
    core = Core()
    
    # بارگذاری پلاگین‌ها
    core.plugin_loader.discover_plugins()
    
    # نمایش دیالوگ لایسنس
    if core.license.license_type == LicenseType.FREE and not core.license.is_school:
        dialog = LicenseDialog(core.license, ScreenOptimizer())
        dialog.exec_()
    
    window = MainWindow(core, core.database, core.license, core.plugin_loader)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
