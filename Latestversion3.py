#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ایمان حسابداری - ImanAccounting
نسخه ۷.۰.۰ - نسخه نهایی برای ارائه در مدرسه
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
import re
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
APP_VERSION = "7.0.0"
APP_AUTHOR = "ایمان"
APP_SLOGAN = "حساب‌هایت رو به ایمان بسپار"
APP_WEBSITE = "iman-accounting.ir"
APP_EMAIL = "neonpresents01@gmail.com"
APP_TELEGRAM = "@ImanAccounting"
APP_SCHOOL = "دبیرستان [اسم مدرسه شما]"
APP_STUDENT = "ایمان [نام خانوادگی] - کلاس دوازدهم حسابداری"

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
        self.type = type  # asset, liability, equity, revenue, expense
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
        self.type = type  # income, expense, transfer
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


# ====================== بهینه‌ساز صفحه نمایش ======================

class ScreenOptimizer:
    """بهینه‌سازی هوشمند برای مینی لپ‌تاپ"""
    
    def __init__(self):
        self.screen = QDesktopWidget().screenGeometry()
        self.width = self.screen.width()
        self.height = self.screen.height()
        self.is_mini = self.width <= 1280 or self.height <= 800
        
        if self.width <= 800:
            self.device_type = "very_small"
        elif self.width <= 1024:
            self.device_type = "small"
        elif self.width <= 1280:
            self.device_type = "medium"
        elif self.width <= 1366:
            self.device_type = "normal"
        else:
            self.device_type = "large"
    
    def get_scale(self) -> float:
        if self.device_type == "very_small":
            return 0.6
        elif self.device_type == "small":
            return 0.7
        elif self.device_type == "medium":
            return 0.8
        elif self.device_type == "normal":
            return 0.9
        return 1.0
    
    def get_font_size(self, base: int = 10) -> int:
        sizes = {
            "very_small": max(9, int(base * 0.9)),
            "small": max(10, int(base * 1.0)),
            "medium": int(base * 1.1),
            "normal": int(base * 1.2),
            "large": int(base * 1.3)
        }
        return sizes.get(self.device_type, base)
    
    def get_window_size(self) -> Tuple[int, int]:
        if self.device_type == "very_small":
            return 950, 600
        elif self.device_type == "small":
            return 1050, 650
        elif self.device_type == "medium":
            return 1150, 700
        elif self.device_type == "normal":
            return 1250, 750
        return 1350, 800
    
    def get_icon_size(self) -> int:
        sizes = {
            "very_small": 22,
            "small": 26,
            "medium": 30,
            "normal": 34,
            "large": 38
        }
        return sizes.get(self.device_type, 26)
    
    def get_card_size(self) -> int:
        sizes = {
            "very_small": 85,
            "small": 95,
            "medium": 105,
            "normal": 115,
            "large": 125
        }
        return sizes.get(self.device_type, 100)
    
    def get_button_height(self) -> int:
        sizes = {
            "very_small": 35,
            "small": 38,
            "medium": 42,
            "normal": 45,
            "large": 48
        }
        return sizes.get(self.device_type, 40)
    
    def get_dialog_size(self) -> Tuple[int, int]:
        sizes = {
            "very_small": (550, 600),
            "small": (600, 650),
            "medium": (650, 700),
            "normal": (700, 750),
            "large": (750, 800)
        }
        return sizes.get(self.device_type, (650, 700))
    
    def get_margin(self) -> int:
        sizes = {
            "very_small": 5,
            "small": 6,
            "medium": 8,
            "normal": 10,
            "large": 12
        }
        return sizes.get(self.device_type, 8)
    
    def get_spacing(self) -> int:
        sizes = {
            "very_small": 5,
            "small": 6,
            "medium": 8,
            "normal": 10,
            "large": 12
        }
        return sizes.get(self.device_type, 8)
    
    def optimize_app(self, app: QApplication):
        print(f"📱 دستگاه: {self.device_type}")
        print(f"📏 صفحه: {self.width} x {self.height}")
        
        try:
            font_names = ["Vazir", "IRANSans", "Tahoma", "Arial", "Sans Serif"]
            selected_font = None
            
            for font_name in font_names:
                if font_name in QFontDatabase().families():
                    selected_font = font_name
                    break
            
            if not selected_font:
                selected_font = "Arial"
            
            font = QFont(selected_font, self.get_font_size())
            app.setFont(font)
            print(f"✅ فونت: {selected_font}")
            
        except Exception as e:
            print(f"⚠️ خطا در تنظیم فونت: {e}")
        
        app.setLayoutDirection(Qt.RightToLeft)


# ====================== سیستم لایسنس ======================

class LicenseType(Enum):
    FREE = "رایگان"
    TRIAL = "آزمایشی"
    PRO = "حرفه‌ای"
    ADMIN = "ادمین"
    SCHOOL = "مدرسه"  # نسخه مخصوص مدرسه


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
        self.school_file = "school.lic"  # لایسنس مخصوص مدرسه
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
        """تولید لایسنس مخصوص مدرسه (بدون محدودیت)"""
        data = {
            'hwid': hwid,
            'type': 'SCHOOL',
            'created': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=3650)).isoformat(),
            'school': APP_SCHOOL
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
            
            key_hash = decoded[:separator]
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
                return True, f"✅ لایسنس مدرسه فعال شد - {data.get('school', '')}", LicenseType.SCHOOL
            
            expiry = datetime.fromisoformat(data['expiry'])
            if expiry < datetime.now():
                return False, f"لایسنس منقضی شده در {expiry.strftime('%Y/%m/%d')}", LicenseType.FREE
            
            if data['type'] == 'PRO':
                return True, "لایسنس حرفه‌ای فعال شد", LicenseType.PRO
            elif data['type'] == 'TRIAL':
                return True, "لایسنس آزمایشی فعال شد", LicenseType.TRIAL
            else:
                return True, "لایسنس فعال شد", LicenseType.FREE
                
        except Exception as e:
            return False, f"خطا: {str(e)}", LicenseType.FREE
    
    def load_license(self):
        # اول چک کن فایل مدرسه هست؟
        if os.path.exists(self.school_file):
            try:
                with open(self.school_file, 'r') as f:
                    license_key = f.read().strip()
                valid, msg, ltype = self.validate_license(license_key)
                if valid:
                    self.license_type = ltype
                    self.license_key = license_key
                    print(f"✅ {msg}")
                    return
            except:
                pass
        
        # بعد چک کن فایل ادمین هست؟
        if os.path.exists(self.admin_file):
            try:
                with open(self.admin_file, 'r') as f:
                    license_key = f.read().strip()
                valid, msg, ltype = self.validate_license(license_key)
                if valid:
                    self.license_type = ltype
                    self.license_key = license_key
                    print(f"✅ {msg}")
                    return
            except:
                pass
        
        # بعد چک کن فایل معمولی هست؟
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    license_key = f.read().strip()
                valid, msg, ltype = self.validate_license(license_key)
                if valid:
                    self.license_type = ltype
                    self.license_key = license_key
                    print(f"✅ {msg}")
                else:
                    print(f"⚠️ {msg}")
                    self.license_type = LicenseType.FREE
            except:
                self.license_type = LicenseType.FREE
        else:
            print("ℹ️ هیچ لایسنسی یافت نشد - نسخه رایگان")
            self.license_type = LicenseType.FREE
    
    def save_license(self, license_key: str, is_admin: bool = False, is_school: bool = False):
        if is_school:
            filename = self.school_file
        elif is_admin:
            filename = self.admin_file
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
        self.accounts = []  # کش در حافظه
        self.transactions = []  # کش در حافظه
        self.init_database()
        self.load_data()
        print(f"📊 {len(self.accounts)} حساب بارگذاری شد")
    
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
            
            # حساب‌های پیش‌فرض - بررسی کن ببینم وجود دارن یا نه
            cursor.execute("SELECT COUNT(*) FROM accounts")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("📝 در حال ایجاد حساب‌های پیش‌فرض...")
                default_accounts = [
                    ('1001', 'وجه نقد', 'asset'),
                    ('1002', 'بانک', 'asset'),
                    ('1101', 'حساب‌های دریافتنی', 'asset'),
                    ('2001', 'حساب‌های پرداختنی', 'liability'),
                    ('3001', 'سرمایه', 'equity'),
                    ('4001', 'فروش', 'revenue'),
                    ('5001', 'هزینه‌ها', 'expense'),
                    ('5002', 'هزینه اجاره', 'expense'),
                    ('5003', 'هزینه حقوق', 'expense'),
                ]
                
                for code, name, type_ in default_accounts:
                    cursor.execute('''
                        INSERT INTO accounts (code, name, type)
                        VALUES (?, ?, ?)
                    ''', (code, name, type_))
                
                conn.commit()
                print(f"✅ {len(default_accounts)} حساب پیش‌فرض ایجاد شد")
    
    def load_data(self):
        """بارگذاری داده‌ها در حافظه"""
        try:
            # پاک کردن لیست قبلی
            self.accounts = []
            self.transactions = []
            
            # بارگذاری حساب‌ها
            accounts_data = self.execute_query("SELECT * FROM accounts WHERE is_active = 1 ORDER BY code")
            print(f"🔍 {len(accounts_data)} حساب از دیتابیس دریافت شد")
            
            for acc in accounts_data:
                account = Account(acc[1], acc[2], acc[3])
                account.id = acc[0]
                account.balance = acc[4] if acc[4] is not None else 0.0
                account.parent_id = acc[5]
                self.accounts.append(account)
            
            # بارگذاری تراکنش‌ها (آخرین ۱۰۰ تا)
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
            
            print(f"✅ {len(self.accounts)} حساب در حافظه بارگذاری شد")
            print(f"✅ {len(self.transactions)} تراکنش در حافظه بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌ها: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def execute_delete(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    # ====================== متدهای مدیریت حساب ======================
    
    def get_all_accounts(self) -> List[Account]:
        """دریافت همه حساب‌های فعال"""
        return self.accounts
    
    def refresh_accounts(self):
        """بروزرسانی لیست حساب‌ها از دیتابیس"""
        try:
            accounts_data = self.execute_query("SELECT * FROM accounts WHERE is_active = 1 ORDER BY code")
            self.accounts = []
            for acc in accounts_data:
                account = Account(acc[1], acc[2], acc[3])
                account.id = acc[0]
                account.balance = acc[4] if acc[4] is not None else 0.0
                account.parent_id = acc[5]
                self.accounts.append(account)
            print(f"🔄 {len(self.accounts)} حساب بروزرسانی شد")
            return True
        except Exception as e:
            print(f"❌ خطا در بروزرسانی حساب‌ها: {e}")
            return False
    
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
        except Exception as e:
            print(f"❌ خطا در افزودن حساب: {e}")
            return False
    
    def update_account_balance(self, account_id: int, amount: float):
        for acc in self.accounts:
            if acc.id == account_id:
                old_balance = acc.balance
                acc.balance = (acc.balance if acc.balance is not None else 0.0) + amount
                self.execute_update(
                    "UPDATE accounts SET balance = ? WHERE id = ?",
                    (acc.balance, account_id)
                )
                print(f"💰 حساب {acc.name}: {old_balance:,.0f} → {acc.balance:,.0f}")
                break
    
    # ====================== متدهای مدیریت تراکنش ======================
    
    def get_all_transactions(self, limit: int = 100) -> List[Transaction]:
        return sorted(self.transactions, key=lambda x: x.date, reverse=True)[:limit]
    
    def refresh_transactions(self):
        """بروزرسانی لیست تراکنش‌ها از دیتابیس"""
        try:
            trans_data = self.execute_query(
                "SELECT * FROM transactions ORDER BY date DESC LIMIT 100"
            )
            self.transactions = []
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
            return True
        except Exception as e:
            print(f"❌ خطا در بروزرسانی تراکنش‌ها: {e}")
            return False
    
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
            
            # به‌روزرسانی موجودی حساب‌ها
            self.update_account_balance(transaction.debit_account_id, transaction.amount)
            self.update_account_balance(transaction.credit_account_id, -transaction.amount)
            
            return True
        except Exception as e:
            print(f"❌ خطا در ثبت تراکنش: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_transactions_by_date(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        result = []
        for trans in self.transactions:
            if start_date <= trans.date <= end_date:
                result.append(trans)
        return sorted(result, key=lambda x: x.date)
    
    def get_total_balance(self) -> float:
        total = 0
        for acc in self.accounts:
            if acc.type == 'asset':
                balance = acc.balance if acc.balance is not None else 0.0
                total += balance
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


# ====================== سیستم پلاگین مبتنی بر امضا ======================

class PluginSignature:
    """مدیریت امضای پلاگین‌ها"""
    
    SIGNATURE = "IMAN_ACCOUNTING_PLUGIN_2024"
    
    @classmethod
    def verify_file(cls, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)
            
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
        self.description = ""
        self.capabilities = []
    
    def get_info(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'capabilities': self.capabilities
        }
    
    def on_load(self, core_proxy):
        self.core = core_proxy
        return True
    
    def on_enable(self):
        pass
    
    def on_disable(self):
        pass
    
    def get_menu_items(self) -> list:
        return []
    
    def get_toolbar_items(self) -> list:
        return []
    
    def get_dashboard_widgets(self) -> list:
        return []
    
    def get_reports(self) -> list:
        return []
    
    def execute(self, command: str, data: dict = None) -> dict:
        return {'success': False, 'message': 'فرمان ناشناخته'}


class PluginLoader:
    """بارگذاری‌کننده پلاگین‌ها با امضا"""
    
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.plugin_folder = "plugins"
        self.backup_folder = os.path.join("plugins", "backup")
        self.create_folders()
    
    def create_folders(self):
        if not os.path.exists(self.plugin_folder):
            os.makedirs(self.plugin_folder)
        
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        
        init_file = os.path.join(self.plugin_folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# پکیج پلاگین‌ها\n")
    
    def discover_plugins(self):
        print("🔍 در حال جستجوی پلاگین‌ها...")
        count = 0
        
        for file in os.listdir(self.plugin_folder):
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(self.plugin_folder, file)
                if self.load_plugin(file_path):
                    count += 1
        
        print(f"✅ {count} پلاگین بارگذاری شد")
        return count
    
    def load_plugin(self, file_path: str) -> bool:
        try:
            if not PluginSignature.verify_file(file_path):
                print(f"❌ {os.path.basename(file_path)}: امضای پلاگین نامعتبر")
                return False
            
            module_name = os.path.basename(file_path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name != 'PluginBase':
                    if hasattr(obj, 'get_info') and hasattr(obj, 'on_load'):
                        plugin_class = obj
                        break
            
            if not plugin_class:
                print(f"❌ {os.path.basename(file_path)}: کلاس پلاگین معتبر یافت نشد")
                return False
            
            plugin_instance = plugin_class()
            
            info = plugin_instance.get_info()
            plugin_id = f"{info.get('name', 'unknown')}_{info.get('version', '0')}"
            
            self.plugins[plugin_id] = {
                'instance': plugin_instance,
                'info': info,
                'file': file_path,
                'filename': os.path.basename(file_path),
                'enabled': True
            }
            
            core_proxy = CoreProxy(self.core)
            plugin_instance.on_load(core_proxy)
            plugin_instance.on_enable()
            
            print(f"✅ پلاگین بارگذاری شد: {info.get('name')} v{info.get('version')}")
            return True
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری {os.path.basename(file_path)}: {e}")
            return False
    
    def import_plugin_from_file(self, file_path: str) -> Tuple[bool, str]:
        try:
            filename = os.path.basename(file_path)
            
            if filename.endswith('.zip'):
                return self._import_from_zip(file_path)
            elif filename.endswith('.py'):
                return self._import_from_py(file_path)
            else:
                return False, "فرمت فایل پشتیبانی نمی‌شود. فقط .py و .zip"
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def _import_from_py(self, file_path: str) -> Tuple[bool, str]:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.plugin_folder, filename)
        
        if not PluginSignature.verify_file(file_path):
            return False, "امضای پلاگین نامعتبر است"
        
        if os.path.exists(dest_path):
            backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(self.backup_folder, backup_name)
            shutil.copy2(dest_path, backup_path)
            os.remove(dest_path)
        
        shutil.copy2(file_path, dest_path)
        
        if self.load_plugin(dest_path):
            return True, f"✅ پلاگین {filename} با موفقیت وارد شد"
        else:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return False, "❌ فایل پلاگین معتبر نیست"
    
    def _import_from_zip(self, zip_path: str) -> Tuple[bool, str]:
        temp_dir = f"temp_plugin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            imported = 0
            errors = []
            
            for file in os.listdir(temp_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    src = os.path.join(temp_dir, file)
                    
                    if not PluginSignature.verify_file(src):
                        errors.append(f"{file} (امضای نامعتبر)")
                        continue
                    
                    dst = os.path.join(self.plugin_folder, file)
                    
                    if os.path.exists(dst):
                        backup_name = f"{file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        backup_path = os.path.join(self.backup_folder, backup_name)
                        shutil.copy2(dst, backup_path)
                        os.remove(dst)
                    
                    shutil.copy2(src, dst)
                    
                    if self.load_plugin(dst):
                        imported += 1
                    else:
                        errors.append(file)
                        if os.path.exists(dst):
                            os.remove(dst)
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if imported > 0:
                if errors:
                    return True, f"✅ {imported} پلاگین وارد شد. {len(errors)} پلاگین مشکل داشت"
                else:
                    return True, f"✅ {imported} پلاگین با موفقیت وارد شد"
            else:
                return False, "❌ هیچ پلاگین معتبری یافت نشد"
                
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, f"خطا: {str(e)}"
    
    def get_all_plugins(self):
        return [p['instance'] for p in self.plugins.values() if p['enabled']]
    
    def get_plugin_menu_items(self):
        items = []
        for plugin in self.get_all_plugins():
            if hasattr(plugin, 'get_menu_items'):
                items.extend(plugin.get_menu_items())
        return items
    
    def get_plugin_toolbar_items(self):
        items = []
        for plugin in self.get_all_plugins():
            if hasattr(plugin, 'get_toolbar_items'):
                items.extend(plugin.get_toolbar_items())
        return items
    
    def get_plugin_dashboard_widgets(self):
        widgets = []
        for plugin in self.get_all_plugins():
            if hasattr(plugin, 'get_dashboard_widgets'):
                widgets.extend(plugin.get_dashboard_widgets())
        return widgets


class CoreProxy:
    """پروکسی هسته برای پلاگین‌ها"""
    
    def __init__(self, core):
        self._core = core
    
    def get_database(self):
        return self._core.database
    
    def get_accounts(self):
        return self._core.database.get_all_accounts()
    
    def get_transactions(self):
        return self._core.database.get_all_transactions()
    
    def add_transaction(self, transaction: Transaction) -> bool:
        return self._core.database.add_transaction(transaction)
    
    def refresh_accounts(self):
        return self._core.database.refresh_accounts()
    
    def get_current_user(self):
        return self._core.current_user
    
    def get_setting(self, key: str, default=None):
        return self._core.settings.get(key, default)
    
    def get_license_info(self):
        return {
            'type': self._core.license.license_type.value,
            'is_admin': self._core.license.is_admin,
            'is_school': self._core.license.is_school,
            'hwid': self._core.license.hardware_id
        }
    
    def get_main_window(self):
        return self._core.main_window
    
    def show_message(self, title: str, message: str, icon: str = 'info'):
        if icon == 'info':
            QMessageBox.information(None, title, message)
        elif icon == 'warning':
            QMessageBox.warning(None, title, message)
        elif icon == 'error':
            QMessageBox.critical(None, title, message)
    
    def add_tab(self, title: str, widget: QWidget):
        if self._core.main_window:
            self._core.main_window.tabs.addTab(widget, title)
    
    def get_optimizer(self):
        return self._core.optimizer


# ====================== ویجت کارت آماری ======================

class StatCard(QFrame):
    """کارت آمار زیبا"""
    
    def __init__(self, title: str, value: str, icon: str, color: str, optimizer: ScreenOptimizer):
        super().__init__()
        self.optimizer = optimizer
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: {self.optimizer.get_margin() * 3}px;
                padding: {self.optimizer.get_margin()}px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(
            self.optimizer.get_margin() * 2,
            self.optimizer.get_margin() * 2,
            self.optimizer.get_margin() * 2,
            self.optimizer.get_margin() * 2
        )
        layout.setSpacing(self.optimizer.get_spacing())
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: {self.optimizer.get_icon_size() * 2}px; background: transparent; color: white;")
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(9)}px; color: rgba(255,255,255,0.9); background: transparent;")
        text_layout.addWidget(title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(16)}px; font-weight: bold; color: white; background: transparent;")
        text_layout.addWidget(self.value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedHeight(self.optimizer.get_card_size() + 10)
    
    def update_value(self, value: str):
        self.value_label.setText(value)


# ====================== دیالوگ ثبت تراکنش (اصلاح شده نهایی) ======================

class TransactionDialog(QDialog):
    """دیالوگ ثبت تراکنش جدید - نسخه نهایی"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        # تعریف تمام متغیرها در ابتدا
        self.date_edit = None
        self.desc_edit = None
        self.type_combo = None
        self.amount_spin = None
        self.debit_combo = None
        self.credit_combo = None
        self.save_btn = None
        self.cancel_btn = None
        
        self.setWindowTitle("➕ ثبت تراکنش جدید")
        self.setFixedSize(500, 450)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
                padding: 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background: white;
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QComboBox {{
                min-height: {self.optimizer.get_button_height() - 10}px;
            }}
            QPushButton {{
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(11)}px;
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
            QPushButton#cancelBtn:hover {{
                background-color: #c0392b;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # فرم
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # تاریخ
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedHeight(self.optimizer.get_button_height())
        form_layout.addRow("📅 تاریخ:", self.date_edit)
        
        # شرح
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        self.desc_edit.setPlaceholderText("شرح تراکنش را وارد کنید...")
        form_layout.addRow("📝 شرح:", self.desc_edit)
        
        # نوع تراکنش
        self.type_combo = QComboBox()
        self.type_combo.addItems(["درآمد", "هزینه", "انتقال"])
        self.type_combo.setFixedHeight(self.optimizer.get_button_height())
        form_layout.addRow("📊 نوع:", self.type_combo)
        
        # مبلغ
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setPrefix("ریال ")
        self.amount_spin.setGroupSeparatorShown(True)
        self.amount_spin.setFixedHeight(self.optimizer.get_button_height())
        form_layout.addRow("💰 مبلغ:", self.amount_spin)
        
        # حساب بدهکار
        self.debit_combo = QComboBox()
        self.debit_combo.setFixedHeight(self.optimizer.get_button_height())
        form_layout.addRow("📤 حساب بدهکار:", self.debit_combo)
        
        # حساب بستانکار
        self.credit_combo = QComboBox()
        self.credit_combo.setFixedHeight(self.optimizer.get_button_height())
        form_layout.addRow("📥 حساب بستانکار:", self.credit_combo)
        
        # حالا که همه کامبوها ساخته شدن، حساب‌ها رو بارگذاری کن
        self.load_accounts()
        
        layout.addLayout(form_layout)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 ذخیره تراکنش")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(self.optimizer.get_button_height())
        self.save_btn.clicked.connect(self.save_transaction)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✖ انصراف")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedHeight(self.optimizer.get_button_height())
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        """بارگذاری لیست حساب‌ها"""
        try:
            # بروزرسانی لیست حساب‌ها از دیتابیس
            self.db.refresh_accounts()
            accounts = self.db.get_all_accounts()
            
            print(f"🔄 بارگذاری {len(accounts)} حساب در دیالوگ تراکنش")
            
            # پاک کردن کامبوها
            if self.debit_combo:
                self.debit_combo.clear()
            if self.credit_combo:
                self.credit_combo.clear()
            
            if len(accounts) == 0:
                print("⚠️ هیچ حسابی یافت نشد!")
                if self.debit_combo:
                    self.debit_combo.addItem("❌ حسابی وجود ندارد", None)
                if self.credit_combo:
                    self.credit_combo.addItem("❌ حسابی وجود ندارد", None)
                return
            
            # اضافه کردن آیتم‌ها
            for acc in accounts:
                if acc.is_active:
                    text = f"{acc.code} - {acc.name}"
                    if self.debit_combo:
                        self.debit_combo.addItem(text, acc.id)
                    if self.credit_combo:
                        self.credit_combo.addItem(text, acc.id)
            
            print(f"✅ {len(accounts)} حساب با موفقیت بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری حساب‌ها: {e}")
            import traceback
            traceback.print_exc()
    
    def save_transaction(self):
        """ذخیره تراکنش"""
        try:
            # اعتبارسنجی
            if self.amount_spin.value() <= 0:
                QMessageBox.warning(self, "خطا", "مبلغ باید بزرگتر از صفر باشد")
                return
            
            # بررسی وجود حساب‌ها
            if not self.debit_combo or not self.credit_combo:
                QMessageBox.warning(self, "خطا", "خطا در بارگذاری حساب‌ها")
                return
            
            if self.debit_combo.count() == 0 or self.credit_combo.count() == 0:
                QMessageBox.warning(self, "خطا", "هیچ حسابی برای انتخاب وجود ندارد.\nلطفاً ابتدا حساب ایجاد کنید.")
                return
            
            debit_id = self.debit_combo.currentData()
            credit_id = self.credit_combo.currentData()
            
            if debit_id is None or credit_id is None:
                QMessageBox.warning(self, "خطا", "لطفاً حساب‌ها را انتخاب کنید")
                return
            
            if debit_id == credit_id:
                QMessageBox.warning(self, "خطا", "حساب بدهکار و بستانکار نمی‌توانند یکسان باشند")
                return
            
            # ایجاد تراکنش
            transaction = Transaction(
                date=self.date_edit.date().toPyDateTime(),
                description=self.desc_edit.toPlainText(),
                amount=self.amount_spin.value(),
                type=self.type_combo.currentText(),
                debit_account_id=debit_id,
                credit_account_id=credit_id
            )
            
            print(f"💾 در حال ثبت تراکنش: {transaction.amount} ریال - {transaction.type}")
            
            # ذخیره
            if self.db.add_transaction(transaction):
                QMessageBox.information(self, "موفق", "✅ تراکنش با موفقیت ثبت شد")
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "❌ خطا در ثبت تراکنش")
                
        except Exception as e:
            print(f"❌ خطا در ذخیره تراکنش: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"خطا در ثبت تراکنش:\n{str(e)}")


# ====================== دیالوگ لیست تراکنش‌ها ======================

class TransactionsListDialog(QDialog):
    """دیالوگ نمایش لیست تراکنش‌ها"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("📋 لیست تراکنش‌ها")
        self.setFixedSize(800, 500)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: {COLORS['light']};
                gridline-color: {COLORS['border']};
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary']};
                color: white;
                padding: 5px;
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: {self.optimizer.get_font_size(10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['info']};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # بروزرسانی لیست تراکنش‌ها
        self.db.refresh_transactions()
        
        # جدول تراکنش‌ها
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره", "تاریخ", "شرح", "نوع", "مبلغ", "بدهکار", "بستانکار"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.load_transactions()
        
        layout.addWidget(self.table)
        
        # دکمه بستن
        close_btn = QPushButton("✖ بستن")
        close_btn.setFixedHeight(self.optimizer.get_button_height())
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_transactions(self):
        """بارگذاری تراکنش‌ها"""
        self.table.setRowCount(0)
        
        accounts = {acc.id: acc for acc in self.db.get_all_accounts()}
        transactions = self.db.get_all_transactions(50)
        
        if len(transactions) == 0:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("هیچ تراکنشی یافت نشد"))
            return
        
        for i, trans in enumerate(transactions):
            self.table.insertRow(i)
            
            self.table.setItem(i, 0, QTableWidgetItem(trans.number))
            self.table.setItem(i, 1, QTableWidgetItem(trans.date.strftime("%Y/%m/%d")))
            desc = trans.description[:30] + "..." if len(trans.description) > 30 else trans.description
            self.table.setItem(i, 2, QTableWidgetItem(desc))
            self.table.setItem(i, 3, QTableWidgetItem(trans.type))
            
            amount_item = QTableWidgetItem(f"{trans.amount:,.0f}")
            amount_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(i, 4, amount_item)
            
            debit_name = accounts.get(trans.debit_account_id, Account("", "", "")).name if trans.debit_account_id in accounts else "نامشخص"
            credit_name = accounts.get(trans.credit_account_id, Account("", "", "")).name if trans.credit_account_id in accounts else "نامشخص"
            
            self.table.setItem(i, 5, QTableWidgetItem(debit_name))
            self.table.setItem(i, 6, QTableWidgetItem(credit_name))


# ====================== دیالوگ لیست حساب‌ها ======================

class AccountsListDialog(QDialog):
    """دیالوگ نمایش لیست حساب‌ها"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("📊 لیست حساب‌ها")
        self.setFixedSize(600, 400)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: {COLORS['light']};
                gridline-color: {COLORS['border']};
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary']};
                color: white;
                padding: 5px;
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: {self.optimizer.get_font_size(10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['info']};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # بروزرسانی لیست حساب‌ها
        self.db.refresh_accounts()
        
        # جدول حساب‌ها
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["کد", "نام", "نوع", "موجودی"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        self.load_accounts()
        
        layout.addWidget(self.table)
        
        # دکمه بستن
        close_btn = QPushButton("✖ بستن")
        close_btn.setFixedHeight(self.optimizer.get_button_height())
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        """بارگذاری حساب‌ها"""
        self.table.setRowCount(0)
        
        accounts = self.db.get_all_accounts()
        type_map = {
            'asset': 'دارایی',
            'liability': 'بدهی',
            'equity': 'سرمایه',
            'revenue': 'درآمد',
            'expense': 'هزینه'
        }
        
        if len(accounts) == 0:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("هیچ حسابی یافت نشد"))
            return
        
        for i, acc in enumerate(accounts):
            if acc.is_active:
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(acc.code))
                self.table.setItem(i, 1, QTableWidgetItem(acc.name))
                self.table.setItem(i, 2, QTableWidgetItem(type_map.get(acc.type, acc.type)))
                
                balance = acc.balance if acc.balance is not None else 0.0
                balance_item = QTableWidgetItem(f"{balance:,.0f}")
                balance_item.setTextAlignment(Qt.AlignRight)
                self.table.setItem(i, 3, balance_item)


# ====================== دیالوگ افزودن حساب ======================

class AddAccountDialog(QDialog):
    """دیالوگ افزودن حساب جدید"""
    
    def __init__(self, db: DatabaseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.db = db
        self.optimizer = optimizer
        
        self.setWindowTitle("➕ افزودن حساب جدید")
        self.setFixedSize(400, 300)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QLineEdit, QComboBox {{
                padding: 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background: white;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton {{
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QPushButton#saveBtn {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton#cancelBtn {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # کد حساب
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("مثلاً 1001")
        layout.addRow("🔢 کد حساب:", self.code_edit)
        
        # نام حساب
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("مثلاً وجه نقد")
        layout.addRow("📝 نام حساب:", self.name_edit)
        
        # نوع حساب
        self.type_combo = QComboBox()
        self.type_combo.addItems(["دارایی", "بدهی", "سرمایه", "درآمد", "هزینه"])
        layout.addRow("📊 نوع حساب:", self.type_combo)
        
        type_map = {
            "دارایی": "asset",
            "بدهی": "liability",
            "سرمایه": "equity",
            "درآمد": "revenue",
            "هزینه": "expense"
        }
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 ذخیره")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(lambda: self.save_account(type_map))
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✖ انصراف")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addRow("", btn_layout)
        
        self.setLayout(layout)
    
    def save_account(self, type_map):
        """ذخیره حساب جدید"""
        code = self.code_edit.text().strip()
        name = self.name_edit.text().strip()
        type_text = self.type_combo.currentText()
        type_ = type_map.get(type_text, "asset")
        
        if not code or not name:
            QMessageBox.warning(self, "خطا", "لطفاً کد و نام حساب را وارد کنید")
            return
        
        account = Account(code, name, type_)
        
        if self.db.add_account(account):
            QMessageBox.information(self, "موفق", f"✅ حساب {name} با موفقیت ایجاد شد")
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", "❌ خطا در ایجاد حساب.\nکد حساب ممکن است تکراری باشد.")


# ====================== دیالوگ لایسنس ======================

class LicenseDialog(QDialog):
    """دیالوگ فعال‌سازی لایسنس"""
    
    def __init__(self, license_manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = ScreenOptimizer()
        
        self.setWindowTitle("🔑 فعال‌سازی لایسنس - ایمان حسابداری")
        width, height = self.optimizer.get_dialog_size()
        self.setFixedSize(width, height)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['primary']};
                border-radius: 10px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background: transparent;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: {COLORS['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['primary']};
            }}
            QTextEdit {{
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                color: {COLORS['text_primary']};
                font-family: monospace;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton {{
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 120px;
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QPushButton#activateBtn {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton#activateBtn:hover {{
                background-color: #229954;
            }}
            QPushButton#buyBtn {{
                background-color: {COLORS['warning']};
                color: white;
            }}
            QPushButton#buyBtn:hover {{
                background-color: #e67e22;
            }}
            QPushButton#closeBtn {{
                background-color: {COLORS['text_secondary']};
                color: white;
            }}
            QPushButton#closeBtn:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing() * 2)
        layout.setContentsMargins(
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3
        )
        
        header_layout = QHBoxLayout()
        logo = QLabel("⚡💰")
        logo.setStyleSheet(f"font-size: {self.optimizer.get_icon_size() * 3}px;")
        header_layout.addWidget(logo)
        
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size: {self.optimizer.get_font_size(20)}px; font-weight: bold; color: {COLORS['primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        hwid_group = QGroupBox("🖥️ شناسه سیستم")
        hwid_layout = QVBoxLayout()
        
        hwid_label = QLabel(self.license.hardware_id)
        hwid_label.setStyleSheet(f"""
            font-family: monospace;
            background-color: {COLORS['light']};
            color: {COLORS['text_primary']};
            padding: 12px;
            border-radius: 5px;
            border: 1px solid {COLORS['border']};
            font-size: {self.optimizer.get_font_size(11)}px;
        """)
        hwid_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        hwid_label.setAlignment(Qt.AlignCenter)
        hwid_layout.addWidget(hwid_label)
        
        hwid_desc = QLabel("این کد را برای دریافت لایسنس ارسال کنید")
        hwid_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {self.optimizer.get_font_size(10)}px;")
        hwid_desc.setAlignment(Qt.AlignCenter)
        hwid_layout.addWidget(hwid_desc)
        
        hwid_group.setLayout(hwid_layout)
        layout.addWidget(hwid_group)
        
        status_group = QGroupBox("📊 وضعیت فعلی")
        status_layout = QFormLayout()
        status_layout.setSpacing(self.optimizer.get_spacing())
        status_layout.setLabelAlignment(Qt.AlignRight)
        
        type_label = QLabel(self.license.license_type.value)
        type_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {self.optimizer.get_font_size(11)}px; font-weight: bold;")
        status_layout.addRow("نوع لایسنس:", type_label)
        
        if self.license.is_admin:
            admin_label = QLabel("ادمین")
            admin_label.setStyleSheet(f"color: {COLORS['warning']}; font-size: {self.optimizer.get_font_size(11)}px; font-weight: bold;")
            status_layout.addRow("دسترسی:", admin_label)
        elif self.license.is_school:
            school_label = QLabel("نسخه مدرسه")
            school_label.setStyleSheet(f"color: {COLORS['success']}; font-size: {self.optimizer.get_font_size(11)}px; font-weight: bold;")
            status_layout.addRow("دسترسی:", school_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        input_group = QGroupBox("🔑 فعال‌سازی")
        input_layout = QVBoxLayout()
        
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("کلید لایسنس را اینجا وارد کنید...")
        self.key_input.setMaximumHeight(100)
        input_layout.addWidget(self.key_input)
        
        btn_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("✅ فعال‌سازی")
        self.activate_btn.setObjectName("activateBtn")
        self.activate_btn.setFixedHeight(self.optimizer.get_button_height())
        self.activate_btn.clicked.connect(self.activate_license)
        btn_layout.addWidget(self.activate_btn)
        
        self.buy_btn = QPushButton("🛒 دریافت لایسنس")
        self.buy_btn.setObjectName("buyBtn")
        self.buy_btn.setFixedHeight(self.optimizer.get_button_height())
        self.buy_btn.clicked.connect(self.buy_license)
        btn_layout.addWidget(self.buy_btn)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedHeight(self.optimizer.get_button_height())
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def activate_license(self):
        license_key = self.key_input.toPlainText().strip()
        if not license_key:
            QMessageBox.warning(self, "خطا", "لطفاً کلید لایسنس را وارد کنید")
            return
        
        valid, message, ltype = self.license.validate_license(license_key)
        
        if valid:
            is_admin = (ltype == LicenseType.ADMIN)
            is_school = (ltype == LicenseType.SCHOOL)
            self.license.save_license(license_key, is_admin, is_school)
            self.license.license_type = ltype
            self.license.is_admin = is_admin
            self.license.is_school = is_school
            QMessageBox.information(self, "موفق", message)
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", message)
    
    def buy_license(self):
        msg = f"""
        برای دریافت لایسنس:

        📧 ایمیل: {APP_EMAIL}
        🌐 وبسایت: {APP_WEBSITE}
        📱 تلگرام: {APP_TELEGRAM}

        🔑 HWID خود را ارسال کنید:
        {self.license.hardware_id}

        💰 قیمت‌ها:
        • نسخه حرفه‌ای: ۵۰۰,۰۰۰ تومان (یک ساله)
        • نسخه آزمایشی: رایگان (۳۰ روز)
        • نسخه مدرسه: رایگان (برای مدارس)
        """
        QMessageBox.information(self, "دریافت لایسنس", msg)


# ====================== دیالوگ درباره ======================

class AboutDialog(QDialog):
    """دیالوگ درباره برنامه"""
    
    def __init__(self, license_manager: LicenseManager, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.license = license_manager
        self.optimizer = optimizer
        
        self.setWindowTitle("ℹ️ درباره ایمان حسابداری")
        width, height = self.optimizer.get_dialog_size()
        self.setFixedSize(width, height)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['primary']};
                border-radius: 10px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background: transparent;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # لوگو
        logo = QLabel("⚡💰")
        logo.setStyleSheet(f"font-size: {self.optimizer.get_icon_size() * 4}px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # عنوان
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size: {self.optimizer.get_font_size(22)}px; font-weight: bold; color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # نسخه
        version = QLabel(f"نسخه {APP_VERSION}")
        version.setStyleSheet(f"font-size: {self.optimizer.get_font_size(14)}px; color: {COLORS['text_secondary']};")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # شعار
        slogan = QLabel(APP_SLOGAN)
        slogan.setStyleSheet(f"font-size: {self.optimizer.get_font_size(12)}px; color: {COLORS['success']}; font-style: italic;")
        slogan.setAlignment(Qt.AlignCenter)
        layout.addWidget(slogan)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(line)
        
        # اطلاعات توسعه‌دهنده
        dev_text = f"""
        👨‍💻 توسعه‌دهنده: {APP_STUDENT}
        🏫 مدرسه: {APP_SCHOOL}
        📅 تاریخ: {datetime.now().strftime('%B %Y')}
        """
        dev_label = QLabel(dev_text)
        dev_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(11)}px;")
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)
        
        # اطلاعات تماس
        contact_text = f"""
        📧 ایمیل: {APP_EMAIL}
        🌐 وبسایت: {APP_WEBSITE}
        📱 تلگرام: {APP_TELEGRAM}
        """
        contact_label = QLabel(contact_text)
        contact_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(11)}px;")
        contact_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact_label)
        
        # وضعیت لایسنس
        license_text = f"🔑 وضعیت لایسنس: {self.license.license_type.value}"
        if self.license.is_school:
            license_text = "🏫 نسخه ویژه مدرسه"
        elif self.license.is_admin:
            license_text = "👑 دسترسی ادمین"
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(11)}px; color: {COLORS['success']}; font-weight: bold;")
        license_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_label)
        
        layout.addStretch()
        
        # دکمه بستن
        close_btn = QPushButton("✖ بستن")
        close_btn.setFixedHeight(self.optimizer.get_button_height())
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: {self.optimizer.get_font_size(12)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['info']};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


# ====================== داشبورد ======================

class DashboardWidget(QWidget):
    """داشبورد اصلی با قابلیت‌های حسابداری"""
    
    def __init__(self, core, db, license_mgr, plugin_loader):
        super().__init__()
        self.core = core
        self.db = db
        self.license = license_mgr
        self.plugin_loader = plugin_loader
        self.optimizer = ScreenOptimizer()
        self.plugin_widgets = []
        
        self.setStyleSheet(f"QWidget {{ background-color: {COLORS['background']}; }}")
        
        self.init_ui()
        self.refresh_data()
        
        # تایمر برای بروزرسانی خودکار
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(60000)  # هر ۱ دقیقه
    
    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(self.optimizer.get_spacing() * 2)
        self.main_layout.setContentsMargins(
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3,
            self.optimizer.get_margin() * 3
        )
        
        # ===== ردیف اول: وضعیت لایسنس و دکمه‌های سریع =====
        top_row = QHBoxLayout()
        
        # وضعیت لایسنس
        license_frame = QFrame()
        license_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: {self.optimizer.get_margin() * 3}px;
                border: 1px solid {COLORS['border']};
                padding: {self.optimizer.get_margin() * 2}px;
            }}
        """)
        
        license_layout = QHBoxLayout()
        
        if self.license.is_admin:
            icon = "👑"
            color = COLORS['warning']
            text = f"{icon} {self.license.license_type.value}"
        elif self.license.is_school:
            icon = "🏫"
            color = COLORS['success']
            text = f"{icon} نسخه مدرسه"
        elif self.license.license_type == LicenseType.PRO:
            icon = "💎"
            color = COLORS['success']
            text = f"{icon} {self.license.license_type.value}"
        elif self.license.license_type == LicenseType.TRIAL:
            icon = "⏳"
            color = COLORS['primary']
            text = f"{icon} {self.license.license_type.value}"
        else:
            icon = "🔓"
            color = COLORS['text_secondary']
            text = f"{icon} {self.license.license_type.value}"
        
        license_label = QLabel(text)
        license_label.setStyleSheet(f"font-size: {self.optimizer.get_font_size(12)}px; font-weight: bold; color: {color};")
        license_layout.addWidget(license_label)
        
        license_frame.setLayout(license_layout)
        top_row.addWidget(license_frame)
        
        # دکمه‌های سریع
        quick_btn_frame = QFrame()
        quick_btn_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: {self.optimizer.get_margin() * 3}px;
                border: 1px solid {COLORS['border']};
                padding: {self.optimizer.get_margin() * 2}px;
            }}
        """)
        
        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.setSpacing(self.optimizer.get_spacing())
        
        # دکمه تراکنش جدید
        trans_btn = QPushButton("➕ تراکنش جدید")
        trans_btn.setFixedHeight(self.optimizer.get_button_height())
        trans_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin() * 2}px;
                padding: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        trans_btn.clicked.connect(self.show_transaction_dialog)
        quick_btn_layout.addWidget(trans_btn)
        
        # دکمه لیست تراکنش‌ها
        list_btn = QPushButton("📋 لیست تراکنش‌ها")
        list_btn.setFixedHeight(self.optimizer.get_button_height())
        list_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin() * 2}px;
                padding: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['info']};
            }}
        """)
        list_btn.clicked.connect(self.show_transactions_list)
        quick_btn_layout.addWidget(list_btn)
        
        # دکمه حساب‌ها
        acc_btn = QPushButton("📊 لیست حساب‌ها")
        acc_btn.setFixedHeight(self.optimizer.get_button_height())
        acc_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['info']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin() * 2}px;
                padding: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        acc_btn.clicked.connect(self.show_accounts_list)
        quick_btn_layout.addWidget(acc_btn)
        
        # دکمه افزودن حساب (برای ادمین و مدرسه)
        if self.license.is_admin or self.license.is_school:
            add_acc_btn = QPushButton("➕ حساب جدید")
            add_acc_btn.setFixedHeight(self.optimizer.get_button_height())
            add_acc_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['warning']};
                    color: white;
                    border: none;
                    border-radius: {self.optimizer.get_margin() * 2}px;
                    padding: {self.optimizer.get_margin() * 2}px;
                    font-size: {self.optimizer.get_font_size(10)}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #e67e22;
                }}
            """)
            add_acc_btn.clicked.connect(self.show_add_account_dialog)
            quick_btn_layout.addWidget(add_acc_btn)
        
        quick_btn_frame.setLayout(quick_btn_layout)
        top_row.addWidget(quick_btn_frame)
        
        self.main_layout.addLayout(top_row)
        
        # ===== ردیف دوم: کارت‌های آماری =====
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(self.optimizer.get_spacing() * 2)
        
        self.total_card = StatCard("موجودی کل", "۰", "💰", COLORS['secondary'], self.optimizer)
        self.stats_layout.addWidget(self.total_card)
        
        self.income_card = StatCard("درآمد امروز", "۰", "📈", COLORS['success'], self.optimizer)
        self.stats_layout.addWidget(self.income_card)
        
        self.expense_card = StatCard("هزینه امروز", "۰", "📉", COLORS['danger'], self.optimizer)
        self.stats_layout.addWidget(self.expense_card)
        
        self.balance_card = StatCard("سود خالص", "۰", "💵", COLORS['warning'], self.optimizer)
        self.stats_layout.addWidget(self.balance_card)
        
        self.main_layout.addLayout(self.stats_layout)
        
        # ===== ردیف سوم: منطقه ویجت‌های پلاگین =====
        self.plugin_area = QVBoxLayout()
        self.main_layout.addLayout(self.plugin_area)
        
        # ===== ردیف چهارم: تراکنش‌های اخیر =====
        recent_group = QGroupBox("🔄 تراکنش‌های اخیر")
        recent_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: {self.optimizer.get_margin() * 2}px;
                margin-top: {self.optimizer.get_margin() * 2}px;
                padding-top: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.optimizer.get_margin() * 3}px;
                padding: 0 {self.optimizer.get_margin()}px 0 {self.optimizer.get_margin()}px;
            }}
        """)
        
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["تاریخ", "شرح", "مبلغ", "نوع"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setMaximumHeight(150)
        self.recent_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                alternate-background-color: {COLORS['light']};
                gridline-color: {COLORS['border']};
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary']};
                color: white;
                padding: 3px;
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
        """)
        
        self.load_recent_transactions()
        
        recent_layout.addWidget(self.recent_table)
        recent_group.setLayout(recent_layout)
        self.main_layout.addWidget(recent_group)
        
        # ===== ردیف پنجم: HWID =====
        hwid_frame = QFrame()
        hwid_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: {self.optimizer.get_margin() * 3}px;
                border: 1px solid {COLORS['border']};
                padding: {self.optimizer.get_margin() * 2}px;
            }}
        """)
        
        hwid_layout = QHBoxLayout()
        hwid_label = QLabel("🖥️ HWID:")
        hwid_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {self.optimizer.get_font_size(11)}px; font-weight: bold;")
        hwid_layout.addWidget(hwid_label)
        
        hwid_value = QLabel(self.license.hardware_id)
        hwid_value.setStyleSheet(f"font-family: monospace; color: {COLORS['text_secondary']}; font-size: {self.optimizer.get_font_size(10)}px; background-color: {COLORS['light']}; padding: 5px; border-radius: 3px;")
        hwid_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        hwid_layout.addWidget(hwid_value)
        hwid_layout.addStretch()
        
        hwid_frame.setLayout(hwid_layout)
        self.main_layout.addWidget(hwid_frame)
        
        self.setLayout(self.main_layout)
    
    def refresh_data(self):
        """به‌روزرسانی آمار"""
        try:
            total = self.db.get_total_balance()
            self.total_card.update_value(f"{total:,.0f}")
            
            income, expense = self.db.get_today_income_expense()
            self.income_card.update_value(f"{income:,.0f}")
            self.expense_card.update_value(f"{expense:,.0f}")
            self.balance_card.update_value(f"{(income - expense):,.0f}")
            
            self.load_recent_transactions()
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی: {e}")
    
    def load_recent_transactions(self):
        """بارگذاری تراکنش‌های اخیر"""
        self.recent_table.setRowCount(0)
        
        self.db.refresh_transactions()
        transactions = self.db.get_all_transactions(10)
        
        if len(transactions) == 0:
            self.recent_table.setRowCount(1)
            self.recent_table.setItem(0, 0, QTableWidgetItem("هیچ تراکنشی ثبت نشده است"))
            return
        
        for i, trans in enumerate(transactions):
            self.recent_table.insertRow(i)
            self.recent_table.setItem(i, 0, QTableWidgetItem(trans.date.strftime("%Y/%m/%d")))
            desc = trans.description[:20] + "..." if len(trans.description) > 20 else trans.description
            self.recent_table.setItem(i, 1, QTableWidgetItem(desc))
            
            amount_item = QTableWidgetItem(f"{trans.amount:,.0f}")
            amount_item.setTextAlignment(Qt.AlignRight)
            self.recent_table.setItem(i, 2, amount_item)
            
            type_item = QTableWidgetItem(trans.type)
            if trans.type == "درآمد":
                type_item.setForeground(QColor(COLORS['success']))
            elif trans.type == "هزینه":
                type_item.setForeground(QColor(COLORS['danger']))
            self.recent_table.setItem(i, 3, type_item)
    
    def show_transaction_dialog(self):
        dialog = TransactionDialog(self.db, self.optimizer, self.window())
        if dialog.exec_():
            self.refresh_data()
    
    def show_transactions_list(self):
        dialog = TransactionsListDialog(self.db, self.optimizer, self.window())
        dialog.exec_()
    
    def show_accounts_list(self):
        dialog = AccountsListDialog(self.db, self.optimizer, self.window())
        dialog.exec_()
    
    def show_add_account_dialog(self):
        dialog = AddAccountDialog(self.db, self.optimizer, self.window())
        if dialog.exec_():
            self.refresh_data()
    
    def add_plugin_widget(self, widget: QWidget):
        self.plugin_area.addWidget(widget)
        self.plugin_widgets.append(widget)


# ====================== دیالوگ وارد کردن پلاگین ======================

class ImportPluginDialog(QDialog):
    """دیالوگ وارد کردن پلاگین از فایل"""
    
    def __init__(self, plugin_loader: PluginLoader, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.plugin_loader = plugin_loader
        self.optimizer = optimizer
        self.selected_file = None
        
        self.setWindowTitle("📥 وارد کردن پلاگین از فایل")
        self.setFixedSize(600, 500)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {COLORS['primary']};
            }}
            QPushButton {{
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton#browseBtn {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QPushButton#importBtn {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton#cancelBtn {{
                background-color: {COLORS['danger']};
                color: white;
            }}
            QTextEdit {{
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-family: monospace;
                font-size: {optimizer.get_font_size(10)}px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing() * 2)
        
        file_group = QGroupBox("۱. انتخاب فایل پلاگین")
        file_layout = QHBoxLayout()
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("فایل پلاگین را انتخاب کنید...")
        self.file_path.setReadOnly(True)
        file_layout.addWidget(self.file_path)
        
        self.browse_btn = QPushButton("🔍 مرور")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setFixedHeight(self.optimizer.get_button_height())
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        info_group = QGroupBox("۲. اطلاعات فایل")
        info_layout = QFormLayout()
        info_layout.setSpacing(self.optimizer.get_spacing())
        
        self.name_label = QLabel("-")
        info_layout.addRow("نام فایل:", self.name_label)
        
        self.type_label = QLabel("-")
        info_layout.addRow("نوع:", self.type_label)
        
        self.size_label = QLabel("-")
        info_layout.addRow("حجم:", self.size_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        preview_group = QGroupBox("۳. پیش‌نمایش امضا")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        result_group = QGroupBox("۴. نتیجه")
        result_layout = QVBoxLayout()
        
        self.result_text = QLabel("")
        self.result_text.setWordWrap(True)
        self.result_text.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        result_group.setVisible(False)
        layout.addWidget(result_group)
        
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📥 وارد کردن")
        self.import_btn.setObjectName("importBtn")
        self.import_btn.setFixedHeight(self.optimizer.get_button_height())
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.import_plugin)
        btn_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("✖ انصراف")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedHeight(self.optimizer.get_button_height())
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل پلاگین",
            os.path.expanduser("~"),
            "فایل‌های پلاگین (*.py *.zip)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path.setText(file_path)
            
            filename = os.path.basename(file_path)
            self.name_label.setText(filename)
            
            file_ext = os.path.splitext(filename)[1].upper()
            self.type_label.setText(f"فایل {file_ext}")
            
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                size_str = f"{file_size} بایت"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.1f} کیلوبایت"
            else:
                size_str = f"{file_size/(1024*1024):.1f} مگابایت"
            self.size_label.setText(size_str)
            
            has_signature = PluginSignature.verify_file(file_path)
            if has_signature:
                self.preview_text.setText("✅ امضای پلاگین معتبر است")
                self.preview_text.setStyleSheet(f"color: {COLORS['success']};")
                self.import_btn.setEnabled(True)
            else:
                self.preview_text.setText("❌ امضای پلاگین نامعتبر است")
                self.preview_text.setStyleSheet(f"color: {COLORS['danger']};")
                self.import_btn.setEnabled(False)
            
            self.result_group.setVisible(False)
    
    def import_plugin(self):
        if not self.selected_file:
            return
        
        progress = QProgressDialog("در حال وارد کردن پلاگین...", "لغو", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setValue(30)
        QApplication.processEvents()
        
        success, message = self.plugin_loader.import_plugin_from_file(self.selected_file)
        
        progress.setValue(100)
        
        self.result_group.setVisible(True)
        if success:
            self.result_text.setText(f"✅ {message}")
            self.result_text.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
            self.import_btn.setEnabled(False)
            
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'refresh_plugin_list'):
                main_window = main_window.parent()
            if main_window and hasattr(main_window, 'refresh_plugin_list'):
                main_window.refresh_plugin_list()
        else:
            self.result_text.setText(f"❌ {message}")
            self.result_text.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold;")


# ====================== دیالوگ مدیریت پلاگین ======================

class PluginManagerDialog(QDialog):
    """دیالوگ مدیریت پلاگین‌ها"""
    
    def __init__(self, plugin_loader: PluginLoader, optimizer: ScreenOptimizer, parent=None):
        super().__init__(parent)
        self.plugin_loader = plugin_loader
        self.optimizer = optimizer
        self.parent_window = parent
        
        self.setWindowTitle("📦 مدیریت پلاگین‌ها")
        self.setFixedSize(700, 500)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['primary']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 8px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['primary']};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: {COLORS['light']};
                gridline-color: {COLORS['border']};
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary']};
                color: white;
                padding: 5px;
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QPushButton {{
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QPushButton#importBtn {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton#refreshBtn {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        list_group = QGroupBox("پلاگین‌های نصب شده")
        list_layout = QVBoxLayout()
        
        self.plugins_table = QTableWidget()
        self.plugins_table.setColumnCount(5)
        self.plugins_table.setHorizontalHeaderLabels(["نام", "نسخه", "نویسنده", "وضعیت", "عملیات"])
        self.plugins_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plugins_table.setAlternatingRowColors(True)
        
        self.load_plugins_list()
        
        list_layout.addWidget(self.plugins_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 وارد کردن پلاگین جدید")
        import_btn.setObjectName("importBtn")
        import_btn.setFixedHeight(self.optimizer.get_button_height())
        import_btn.clicked.connect(self.show_import_dialog)
        btn_layout.addWidget(import_btn)
        
        refresh_btn = QPushButton("🔄 بروزرسانی لیست")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.setFixedHeight(self.optimizer.get_button_height())
        refresh_btn.clicked.connect(self.load_plugins_list)
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.setFixedHeight(self.optimizer.get_button_height())
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_plugins_list(self):
        self.plugins_table.setRowCount(0)
        
        row = 0
        for plugin_id, plugin in self.plugin_loader.plugins.items():
            info = plugin['info']
            self.plugins_table.insertRow(row)
            
            self.plugins_table.setItem(row, 0, QTableWidgetItem(info.get('name', 'ناشناس')))
            self.plugins_table.setItem(row, 1, QTableWidgetItem(info.get('version', '0')))
            self.plugins_table.setItem(row, 2, QTableWidgetItem(info.get('author', 'ناشناس')))
            
            status = "✅ فعال" if plugin['enabled'] else "❌ غیرفعال"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(COLORS['success'] if plugin['enabled'] else COLORS['danger']))
            self.plugins_table.setItem(row, 3, status_item)
            
            toggle_btn = QPushButton("غیرفعال" if plugin['enabled'] else "فعال")
            toggle_btn.clicked.connect(lambda checked, pid=plugin_id: self.toggle_plugin(pid))
            self.plugins_table.setCellWidget(row, 4, toggle_btn)
            
            row += 1
        
        if row == 0:
            self.plugins_table.setRowCount(1)
            self.plugins_table.setItem(0, 0, QTableWidgetItem("هیچ پلاگینی نصب نشده است"))
    
    def toggle_plugin(self, plugin_id: str):
        plugin = self.plugin_loader.plugins.get(plugin_id)
        if plugin:
            if plugin['enabled']:
                plugin['enabled'] = False
                plugin['instance'].on_disable()
            else:
                plugin['enabled'] = True
                plugin['instance'].on_enable()
            
            self.load_plugins_list()
            
            QMessageBox.information(
                self, 
                "تغییر وضعیت",
                f"وضعیت پلاگین تغییر کرد.\nبرای اعمال تغییرات برنامه را مجدداً اجرا کنید."
            )
    
    def show_import_dialog(self):
        dialog = ImportPluginDialog(self.plugin_loader, self.optimizer, self)
        if dialog.exec_():
            self.load_plugins_list()


# ====================== پنجره اصلی ======================

class MainWindow(QMainWindow):
    """پنجره اصلی برنامه با پشتیبانی از پلاگین"""
    
    def __init__(self, core, db, license_mgr, plugin_loader):
        super().__init__()
        self.core = core
        self.db = db
        self.license = license_mgr
        self.plugin_loader = plugin_loader
        self.optimizer = ScreenOptimizer()
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QMenuBar {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                font-size: {self.optimizer.get_font_size(10)}px;
                padding: {self.optimizer.get_margin()}px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: {self.optimizer.get_margin() * 2}px {self.optimizer.get_margin() * 3}px;
            }}
            QMenuBar::item:selected {{
                background: {COLORS['primary']};
                border-radius: {self.optimizer.get_margin()}px;
            }}
            QMenu {{
                background-color: white;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabWidget::pane {{
                background-color: {COLORS['background']};
                border: none;
            }}
            QTabBar::tab {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                padding: {self.optimizer.get_margin() * 2}px {self.optimizer.get_margin() * 4}px;
                margin-right: 2px;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: {self.optimizer.get_margin() * 2}px;
                border-top-right-radius: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(10)}px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['light']};
            }}
            QStatusBar {{
                background-color: {COLORS['secondary']};
                color: white;
                font-size: {self.optimizer.get_font_size(9)}px;
            }}
            QToolBar {{
                background-color: {COLORS['card_bg']};
                border: none;
                spacing: {self.optimizer.get_spacing()}px;
                padding: {self.optimizer.get_margin()}px;
            }}
        """)
        
        w, h = self.optimizer.get_window_size()
        self.resize(w, h)
        
        title = APP_NAME
        if self.license.is_admin:
            title += " [ادمین]"
        elif self.license.is_school:
            title += " [نسخه مدرسه]"
        elif self.license.license_type != LicenseType.FREE:
            title += f" [{self.license.license_type.value}]"
        
        self.setWindowTitle(title)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        self.optimizer.optimize_app(QApplication.instance())
        
        self.init_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
        
        self.apply_plugins()
    
    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        self.dashboard = DashboardWidget(self.core, self.db, self.license, self.plugin_loader)
        self.tabs.addTab(self.dashboard, "🏠 داشبورد")
        
        self.tabs.addTab(QWidget(), "📊 گزارشات")
        self.tabs.addTab(QWidget(), "⚙️ تنظیمات")
        
        self.plugin_manager_tab = self.create_plugin_manager_tab()
        self.tabs.addTab(self.plugin_manager_tab, "📦 پلاگین‌ها")
        
        if self.license.is_admin or self.license.is_school:
            admin_tab = self.create_admin_tab()
            self.tabs.addTab(admin_tab, "⚙️ مدیریت")
        
        self.setCentralWidget(self.tabs)
    
    def create_plugin_manager_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        
        import_btn = QPushButton("📥 وارد کردن پلاگین جدید از فایل")
        import_btn.setFixedHeight(self.optimizer.get_button_height())
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(11)}px;
                font-weight: bold;
                padding: {self.optimizer.get_margin() * 2}px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        import_btn.clicked.connect(self.show_import_dialog)
        layout.addWidget(import_btn)
        
        manage_btn = QPushButton("📋 مدیریت پلاگین‌ها")
        manage_btn.setFixedHeight(self.optimizer.get_button_height())
        manage_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(11)}px;
                font-weight: bold;
                padding: {self.optimizer.get_margin() * 2}px;
                margin-top: {self.optimizer.get_margin()}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['info']};
            }}
        """)
        manage_btn.clicked.connect(self.show_plugin_manager_dialog)
        layout.addWidget(manage_btn)
        
        self.plugin_list = QListWidget()
        self.plugin_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: {self.optimizer.get_margin() * 2}px;
                padding: {self.optimizer.get_margin()}px;
                font-size: {self.optimizer.get_font_size(10)}px;
                margin-top: {self.optimizer.get_margin() * 2}px;
            }}
            QListWidget::item {{
                padding: {self.optimizer.get_margin() * 2}px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        
        self.refresh_plugin_list()
        layout.addWidget(self.plugin_list)
        
        refresh_btn = QPushButton("🔄 بروزرسانی لیست")
        refresh_btn.setFixedHeight(self.optimizer.get_button_height())
        refresh_btn.clicked.connect(self.refresh_plugin_list)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_plugin_list(self):
        self.plugin_list.clear()
        
        for plugin_id, plugin in self.plugin_loader.plugins.items():
            info = plugin['info']
            status = "✅" if plugin['enabled'] else "❌"
            item_text = f"{status} {info.get('name', 'ناشناس')} v{info.get('version', '0')} - {info.get('author', 'ناشناس')}"
            self.plugin_list.addItem(item_text)
        
        if not self.plugin_loader.plugins:
            self.plugin_list.addItem("هیچ پلاگینی نصب نشده است")
    
    def create_admin_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(self.optimizer.get_spacing() * 2)
        
        info_group = QGroupBox("اطلاعات مدیریت")
        info_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['warning']};
                border-radius: {self.optimizer.get_margin() * 2}px;
                margin-top: {self.optimizer.get_margin() * 3}px;
                padding-top: {self.optimizer.get_margin() * 2}px;
                font-size: {self.optimizer.get_font_size(11)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {COLORS['warning']};
            }}
        """)
        
        info_layout = QFormLayout()
        
        if self.license.is_admin:
            access_text = "ادمین کامل"
            access_color = COLORS['warning']
        elif self.license.is_school:
            access_text = "مدیر مدرسه"
            access_color = COLORS['success']
        else:
            access_text = "کاربر عادی"
            access_color = COLORS['text_primary']
        
        access_label = QLabel(access_text)
        access_label.setStyleSheet(f"color: {access_color}; font-weight: bold;")
        info_layout.addRow("نوع دسترسی:", access_label)
        
        hwid_label = QLabel(self.license.hardware_id)
        hwid_label.setStyleSheet(f"font-family: monospace; color: {COLORS['text_primary']};")
        hwid_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addRow("HWID:", hwid_label)
        
        license_label = QLabel(self.license.license_type.value)
        license_label.setStyleSheet(f"color: {COLORS['success']};")
        info_layout.addRow("لایسنس:", license_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        if self.license.is_admin:
            tools_group = QGroupBox("ابزارهای ادمین")
            tools_group.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {COLORS['primary']};
                    border-radius: {self.optimizer.get_margin() * 2}px;
                    margin-top: {self.optimizer.get_margin() * 3}px;
                    padding-top: {self.optimizer.get_margin() * 2}px;
                    font-size: {self.optimizer.get_font_size(11)}px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: {COLORS['primary']};
                }}
            """)
            
            tools_layout = QVBoxLayout()
            
            generate_btn = QPushButton("🔑 تولید لایسنس برای کاربر")
            generate_btn.setFixedHeight(self.optimizer.get_button_height())
            generate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: {self.optimizer.get_margin() * 2}px;
                    padding: {self.optimizer.get_margin() * 2}px;
                    font-size: {self.optimizer.get_font_size(11)}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['info']};
                }}
            """)
            generate_btn.clicked.connect(self.generate_user_license)
            tools_layout.addWidget(generate_btn)
            
            tools_group.setLayout(tools_layout)
            layout.addWidget(tools_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("فایل")
        
        license_action = QAction("🔑 فعال‌سازی لایسنس", self)
        license_action.triggered.connect(self.show_license_dialog)
        file_menu.addAction(license_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        accounting_menu = menubar.addMenu("💰 حسابداری")
        
        trans_action = QAction("➕ تراکنش جدید", self)
        trans_action.triggered.connect(self.dashboard.show_transaction_dialog)
        accounting_menu.addAction(trans_action)
        
        list_action = QAction("📋 لیست تراکنش‌ها", self)
        list_action.triggered.connect(self.dashboard.show_transactions_list)
        accounting_menu.addAction(list_action)
        
        accounts_action = QAction("📊 لیست حساب‌ها", self)
        accounts_action.triggered.connect(self.dashboard.show_accounts_list)
        accounting_menu.addAction(accounts_action)
        
        if self.license.is_admin or self.license.is_school:
            add_account_action = QAction("➕ حساب جدید", self)
            add_account_action.triggered.connect(self.dashboard.show_add_account_dialog)
            accounting_menu.addAction(add_account_action)
        
        plugin_menu = menubar.addMenu("📦 پلاگین")
        
        import_action = QAction("📥 وارد کردن پلاگین از فایل", self)
        import_action.triggered.connect(self.show_import_dialog)
        plugin_menu.addAction(import_action)
        
        plugin_menu.addSeparator()
        
        manage_action = QAction("📋 مدیریت پلاگین‌ها", self)
        manage_action.triggered.connect(self.show_plugin_manager_dialog)
        plugin_menu.addAction(manage_action)
        
        help_menu = menubar.addMenu("راهنما")
        
        about_action = QAction("ℹ️ درباره", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = self.addToolBar("ابزارها")
        toolbar.setMovable(False)
        
        icon_size = self.optimizer.get_icon_size()
        toolbar.setIconSize(QSize(icon_size, icon_size))
        
        trans_btn = QAction("➕", self)
        trans_btn.setToolTip("تراکنش جدید")
        trans_btn.triggered.connect(self.dashboard.show_transaction_dialog)
        toolbar.addAction(trans_btn)
        
        list_btn = QAction("📋", self)
        list_btn.setToolTip("لیست تراکنش‌ها")
        list_btn.triggered.connect(self.dashboard.show_transactions_list)
        toolbar.addAction(list_btn)
        
        accounts_btn = QAction("📊", self)
        accounts_btn.setToolTip("لیست حساب‌ها")
        accounts_btn.triggered.connect(self.dashboard.show_accounts_list)
        toolbar.addAction(accounts_btn)
        
        if self.license.is_admin or self.license.is_school:
            add_acc_btn = QAction("➕📊", self)
            add_acc_btn.setToolTip("حساب جدید")
            add_acc_btn.triggered.connect(self.dashboard.show_add_account_dialog)
            toolbar.addAction(add_acc_btn)
        
        toolbar.addSeparator()
        
        license_btn = QAction("🔑", self)
        license_btn.setToolTip("فعال‌سازی لایسنس")
        license_btn.triggered.connect(self.show_license_dialog)
        toolbar.addAction(license_btn)
        
        import_btn = QAction("📥", self)
        import_btn.setToolTip("وارد کردن پلاگین")
        import_btn.triggered.connect(self.show_import_dialog)
        toolbar.addAction(import_btn)
        
        about_btn = QAction("ℹ️", self)
        about_btn.setToolTip("درباره برنامه")
        about_btn.triggered.connect(self.show_about)
        toolbar.addAction(about_btn)
        
        toolbar.addSeparator()
    
    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        if self.license.is_admin:
            status_text = "👑 ادمین"
            color = COLORS['warning']
        elif self.license.is_school:
            status_text = "🏫 نسخه مدرسه"
            color = COLORS['success']
        else:
            status_text = f"🔑 {self.license.license_type.value}"
            color = COLORS['text_light']
        
        license_label = QLabel(status_text)
        license_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: {self.optimizer.get_font_size(9)}px;")
        self.statusbar.addPermanentWidget(license_label)
        
        plugin_count = len(self.plugin_loader.plugins)
        plugin_label = QLabel(f"📦 {plugin_count} پلاگین")
        plugin_label.setStyleSheet(f"color: white; font-size: {self.optimizer.get_font_size(9)}px;")
        self.statusbar.addPermanentWidget(plugin_label)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"color: white; font-size: {self.optimizer.get_font_size(9)}px;")
        self.statusbar.addPermanentWidget(self.date_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
        
        self.update_status()
    
    def update_status(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("yyyy/MM/dd HH:mm"))
    
    def apply_plugins(self):
        """اعمال قابلیت‌های پلاگین‌ها"""
        for item in self.plugin_loader.get_plugin_menu_items():
            self.add_plugin_menu_item(item)
        
        for item in self.plugin_loader.get_plugin_toolbar_items():
            self.add_plugin_toolbar_item(item)
        
        for widget_info in self.plugin_loader.get_plugin_dashboard_widgets():
            try:
                if isinstance(widget_info, dict) and 'class' in widget_info:
                    widget_class = widget_info['class']
                    widget = widget_class(self.core, self.dashboard)
                    self.dashboard.add_plugin_widget(widget)
                elif callable(widget_info):
                    widget = widget_info(self.core, self.dashboard)
                    self.dashboard.add_plugin_widget(widget)
            except Exception as e:
                print(f"⚠️ خطا در ایجاد ویجت پلاگین: {e}")
    
    def add_plugin_menu_item(self, item):
        try:
            if isinstance(item, dict):
                path_parts = item.get('path', '').split('/')
                title = item.get('title', '')
                callback = item.get('callback', None)
                shortcut = item.get('shortcut', None)
                
                if not path_parts or not title or not callback:
                    return
                
                menu = self.menuBar()
                for part in path_parts[:-1]:
                    found = False
                    for action in menu.actions():
                        if action.text() == part and action.menu():
                            menu = action.menu()
                            found = True
                            break
                    if not found:
                        new_menu = menu.addMenu(part)
                        menu = new_menu
                
                action = QAction(title, self)
                action.triggered.connect(callback)
                
                if shortcut:
                    action.setShortcut(shortcut)
                
                menu.addAction(action)
        except Exception as e:
            print(f"⚠️ خطا در اضافه کردن آیتم منو: {e}")
    
    def add_plugin_toolbar_item(self, item):
        try:
            if isinstance(item, dict):
                title = item.get('title', '')
                callback = item.get('callback', None)
                tooltip = item.get('tooltip', '')
                
                if not title or not callback:
                    return
                
                toolbar = self.findChild(QToolBar, "ابزارها")
                if toolbar:
                    action = QAction(title, self)
                    action.triggered.connect(callback)
                    action.setToolTip(tooltip)
                    toolbar.addAction(action)
        except Exception as e:
            print(f"⚠️ خطا در اضافه کردن دکمه نوار ابزار: {e}")
    
    def show_license_dialog(self):
        dialog = LicenseDialog(self.license, self)
        if dialog.exec_():
            QMessageBox.information(self, "موفق", "✅ لایسنس فعال شد. برنامه را مجدداً اجرا کنید.")
            QApplication.quit()
    
    def show_import_dialog(self):
        dialog = ImportPluginDialog(self.plugin_loader, self.optimizer, self)
        if dialog.exec_():
            self.refresh_plugin_list()
    
    def show_plugin_manager_dialog(self):
        dialog = PluginManagerDialog(self.plugin_loader, self.optimizer, self)
        if dialog.exec_():
            self.refresh_plugin_list()
    
    def generate_user_license(self):
        if not self.license.is_admin:
            QMessageBox.warning(self, "خطا", "فقط ادمین می‌تواند لایسنس تولید کند")
            return
        
        hwid, ok = QInputDialog.getText(self, "تولید لایسنس", "HWID کاربر را وارد کنید:")
        if not ok or not hwid:
            return
        
        items = ["آزمایشی (۳۰ روز)", "حرفه‌ای (یک سال)", "مدرسه (نامحدود)"]
        item, ok = QInputDialog.getItem(self, "نوع لایسنس", "نوع لایسنس را انتخاب کنید:", items, 0, False)
        if not ok:
            return
        
        if "مدرسه" in item:
            license_key = self.license.generate_school_license(hwid)
            ltype = "SCHOOL"
        else:
            days = 30 if "آزمایشی" in item else 365
            ltype = "TRIAL" if "آزمایشی" in item else "PRO"
            license_key = self.license.generate_user_license(hwid, ltype, days)
        
        filename = f"license_{hwid[:8]}.lic"
        with open(filename, 'w') as f:
            f.write(license_key)
        
        QMessageBox.information(
            self, 
            "✅ لایسنس ساخته شد", 
            f"✅ لایسنس در فایل {filename} ذخیره شد.\n\n{license_key}"
        )
    
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
        self.settings = {}
        self.main_window = None
        self.optimizer = ScreenOptimizer()
        self.current_user = {"name": "کاربر", "role": "user"}


# ====================== تابع اصلی ======================

def main():
    app = QApplication(sys.argv)
    
    core = Core()
    core.optimizer.optimize_app(app)
    
    # اگر لایسنس مدرسه یا ادمین نبود و نسخه رایگان بود، دیالوگ لایسنس رو نشون بده
    if not core.license.is_school and not core.license.is_admin and core.license.license_type == LicenseType.FREE:
        splash = QSplashScreen()
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        pixmap = QPixmap(450, 250)
        pixmap.fill(QColor(COLORS['secondary']))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Vazir", 18, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{APP_NAME}\n\nبه برنامه خوش آمدید")
        painter.end()
        
        splash.setPixmap(pixmap)
        splash.show()
        
        def show_dialog():
            splash.close()
            dialog = LicenseDialog(core.license)
            if dialog.exec_() == QDialog.Accepted:
                core.plugin_loader.discover_plugins()
                window = MainWindow(core, core.database, core.license, core.plugin_loader)
                core.main_window = window
                window.show()
            else:
                core.plugin_loader.discover_plugins()
                window = MainWindow(core, core.database, core.license, core.plugin_loader)
                core.main_window = window
                window.show()
        
        QTimer.singleShot(1000, show_dialog)
        
        sys.exit(app.exec_())
    else:
        core.plugin_loader.discover_plugins()
        window = MainWindow(core, core.database, core.license, core.plugin_loader)
        core.main_window = window
        window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()