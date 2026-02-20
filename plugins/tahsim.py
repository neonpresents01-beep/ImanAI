#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
پلاگین تسهیم - ImanAccounting Plugin
محاسبه تسهیم سود و زیان بین شرکا
مناسب برای ارائه در مدرسه
نسخه ۱.۰.۰
"""

PLUGIN_SIGNATURE = "IMAN_ACCOUNTING_PLUGIN_2024"

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
from datetime import datetime


class TahsimPlugin:
    """پلاگین محاسبه تسهیم"""
    
    def __init__(self):
        self.name = "پلاگین تسهیم"
        self.version = "1.0.0"
        self.author = "ایمان - هنرستان"
        self.description = "محاسبه تسهیم سود و زیان بین شرکا - مخصوص ارائه مدرسه"
        self.capabilities = ["dashboard", "menu", "report"]
        self.core = None
        
        # رنگ‌های اختصاصی پلاگین
        self.colors = {
            'primary': '#27ae60',
            'secondary': '#2980b9',
            'accent': '#f39c12',
            'danger': '#e74c3c'
        }
    
    def get_info(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'capabilities': self.capabilities
        }
    
    def on_load(self, core_proxy):
        """وقتی پلاگین بارگذاری میشه"""
        self.core = core_proxy
        print(f"✅ پلاگین {self.name} با موفقیت بارگذاری شد")
        return True
    
    def on_enable(self):
        """وقتی پلاگین فعال میشه"""
        print(f"✅ پلاگین {self.name} فعال شد")
    
    def on_disable(self):
        """وقتی پلاگین غیرفعال میشه"""
        print(f"⚠️ پلاگین {self.name} غیرفعال شد")
    
    def get_menu_items(self) -> list:
        """آیتم‌های منو"""
        return [
            {
                'path': '💰 حسابداری/تسهیم',
                'title': '🧮 محاسبه تسهیم',
                'callback': self.show_tahsim_dialog,
                'shortcut': 'Ctrl+T'
            },
            {
                'path': '📊 گزارشات/تسهیم',
                'title': '📈 گزارش تسهیم',
                'callback': self.show_tahsim_report
            }
        ]
    
    def get_toolbar_items(self) -> list:
        """دکمه‌های نوار ابزار"""
        return [
            {
                'title': '🧮 تسهیم',
                'callback': self.show_tahsim_dialog,
                'tooltip': 'محاسبه تسهیم سود و زیان'
            }
        ]
    
    def get_dashboard_widgets(self) -> list:
        """ویجت‌های داشبورد"""
        return [
            {
                'class': TahsimWidget,
                'position': 'top'
            }
        ]
    
    def get_reports(self) -> list:
        """گزارش‌های قابل چاپ"""
        return [
            {
                'name': 'گزارش تسهیم',
                'callback': self.generate_tahsim_report
            }
        ]
    
    def show_tahsim_dialog(self):
        """نمایش دیالوگ محاسبه تسهیم"""
        dialog = TahsimDialog(self.core, self)
        dialog.exec_()
    
    def show_tahsim_report(self):
        """نمایش گزارش تسهیم"""
        report = TahsimReportDialog(self.core, self)
        report.exec_()
    
    def generate_tahsim_report(self, data: dict = None):
        """تولید گزارش تسهیم"""
        if not data:
            data = self.get_default_data()
        
        report_text = f"""
        📊 گزارش تسهیم سود و زیان
        ============================
        تاریخ: {datetime.now().strftime('%Y/%m/%d')}
        
        💰 کل سود: {data.get('total_profit', 0):,} ریال
        
        👥 تسهیم بین شرکا:
        """
        
        for i, partner in enumerate(data.get('partners', []), 1):
            report_text += f"\n        {i}. {partner['name']}: {partner['share']:,} ریال ({partner['percent']}%)"
        
        return report_text
    
    def get_default_data(self):
        """داده‌های پیش‌فرض برای تست"""
        return {
            'total_profit': 10000000,
            'partners': [
                {'name': 'شریک اول', 'percent': 40, 'share': 4000000},
                {'name': 'شریک دوم', 'percent': 35, 'share': 3500000},
                {'name': 'شریک سوم', 'percent': 25, 'share': 2500000}
            ]
        }


class TahsimWidget(QWidget):
    """ویجت داشبورد برای نمایش تسهیم"""
    
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        self.plugin = parent if isinstance(parent, TahsimPlugin) else None
        
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # عنوان
        title = QLabel("🧮 تسهیم سود و زیان")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        layout.addWidget(title)
        
        # اطلاعات
        info_label = QLabel("محاسبه سهم شرکا از سود")
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(info_label)
        
        # دکمه محاسبه
        calc_btn = QPushButton("محاسبه تسهیم")
        calc_btn.clicked.connect(self.show_tahsim)
        layout.addWidget(calc_btn)
        
        self.setLayout(layout)
        self.setFixedHeight(120)
    
    def show_tahsim(self):
        if self.plugin:
            self.plugin.show_tahsim_dialog()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "تسهیم", "پلاگین تسهیم فعال است")


class TahsimDialog(QDialog):
    """دیالوگ اصلی محاسبه تسهیم"""
    
    def __init__(self, core, plugin, parent=None):
        super().__init__(parent)
        self.core = core
        self.plugin = plugin
        self.partners = []
        
        self.setWindowTitle("🧮 محاسبه تسهیم سود و زیان")
        self.setFixedSize(600, 500)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #27ae60;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton#addBtn {
                background-color: #27ae60;
                color: white;
            }
            QPushButton#calcBtn {
                background-color: #2980b9;
                color: white;
            }
            QPushButton#removeBtn {
                background-color: #e74c3c;
                color: white;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
            }
        """)
        
        self.init_ui()
        self.add_sample_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # گروه اطلاعات
        info_group = QGroupBox("💰 اطلاعات سود")
        info_layout = QFormLayout()
        
        self.profit_spin = QSpinBox()
        self.profit_spin.setRange(0, 1000000000)
        self.profit_spin.setValue(10000000)
        self.profit_spin.setSuffix(" ریال")
        self.profit_spin.setGroupSeparatorShown(True)
        info_layout.addRow("کل سود:", self.profit_spin)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # گروه شرکا
        partners_group = QGroupBox("👥 شرکا")
        partners_layout = QVBoxLayout()
        
        # فرم افزودن شریک
        add_layout = QHBoxLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("نام شریک")
        add_layout.addWidget(self.name_edit)
        
        self.percent_spin = QSpinBox()
        self.percent_spin.setRange(1, 100)
        self.percent_spin.setValue(20)
        self.percent_spin.setSuffix(" %")
        add_layout.addWidget(self.percent_spin)
        
        add_btn = QPushButton("➕ افزودن شریک")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.add_partner)
        add_layout.addWidget(add_btn)
        
        partners_layout.addLayout(add_layout)
        
        # جدول شرکا
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["نام", "درصد", "سهم (ریال)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        partners_layout.addWidget(self.table)
        
        partners_group.setLayout(partners_layout)
        layout.addWidget(partners_group)
        
        # دکمه‌های عملیات
        btn_layout = QHBoxLayout()
        
        calc_btn = QPushButton("🧮 محاسبه تسهیم")
        calc_btn.setObjectName("calcBtn")
        calc_btn.clicked.connect(self.calculate_tahsim)
        btn_layout.addWidget(calc_btn)
        
        report_btn = QPushButton("📊 گزارش")
        report_btn.setObjectName("calcBtn")
        report_btn.clicked.connect(self.show_report)
        btn_layout.addWidget(report_btn)
        
        remove_btn = QPushButton("🗑️ حذف آخرین")
        remove_btn.setObjectName("removeBtn")
        remove_btn.clicked.connect(self.remove_last)
        btn_layout.addWidget(remove_btn)
        
        close_btn = QPushButton("✖ بستن")
        close_btn.setObjectName("removeBtn")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_sample_data(self):
        """افزودن داده نمونه برای تست"""
        self.partners = [
            {'name': 'احمدی', 'percent': 40},
            {'name': 'محمدی', 'percent': 35},
            {'name': 'کریمی', 'percent': 25}
        ]
        self.refresh_table()
    
    def add_partner(self):
        """افزودن شریک جدید"""
        name = self.name_edit.text().strip()
        percent = self.percent_spin.value()
        
        if not name:
            QMessageBox.warning(self, "خطا", "لطفاً نام شریک را وارد کنید")
            return
        
        # بررسی مجموع درصدها
        total_percent = sum(p['percent'] for p in self.partners) + percent
        if total_percent > 100:
            QMessageBox.warning(self, "خطا", f"مجموع درصدها نمی‌تواند از ۱۰۰ بیشتر باشد.\nدر حال حاضر: {total_percent - percent}% + {percent}% = {total_percent}%")
            return
        
        self.partners.append({'name': name, 'percent': percent})
        self.name_edit.clear()
        self.percent_spin.setValue(20)
        self.refresh_table()
    
    def remove_last(self):
        """حذف آخرین شریک"""
        if self.partners:
            self.partners.pop()
            self.refresh_table()
    
    def refresh_table(self):
        """بروزرسانی جدول"""
        self.table.setRowCount(len(self.partners))
        profit = self.profit_spin.value()
        
        for i, partner in enumerate(self.partners):
            share = profit * partner['percent'] // 100
            
            self.table.setItem(i, 0, QTableWidgetItem(partner['name']))
            
            percent_item = QTableWidgetItem(f"{partner['percent']}%")
            percent_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, percent_item)
            
            share_item = QTableWidgetItem(f"{share:,}")
            share_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(i, 2, share_item)
    
    def calculate_tahsim(self):
        """محاسبه و نمایش تسهیم"""
        self.refresh_table()
        
        if not self.partners:
            QMessageBox.warning(self, "خطا", "هیچ شریکی تعریف نشده")
            return
        
        profit = self.profit_spin.value()
        total_percent = sum(p['percent'] for p in self.partners)
        
        if total_percent != 100:
            QMessageBox.warning(self, "خطا", f"مجموع درصدها باید ۱۰۰ باشد.\nدر حال حاضر: {total_percent}%")
            return
        
        # نمایش نتیجه
        result = f"💰 سود کل: {profit:,} ریال\n\n"
        result += "📊 سهم شرکا:\n"
        result += "-" * 30 + "\n"
        
        for partner in self.partners:
            share = profit * partner['percent'] // 100
            result += f"{partner['name']}: {share:,} ریال ({partner['percent']}%)\n"
        
        QMessageBox.information(self, "✅ نتیجه تسهیم", result)
    
    def show_report(self):
        """نمایش گزارش"""
        self.calculate_tahsim()
        # اینجا می‌تونه گزارش PDF هم بگیره


class TahsimReportDialog(QDialog):
    """دیالوگ گزارش تسهیم"""
    
    def __init__(self, core, plugin, parent=None):
        super().__init__(parent)
        self.core = core
        self.plugin = plugin
        
        self.setWindowTitle("📊 گزارش تسهیم")
        self.setFixedSize(500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid #27ae60;
                border-radius: 8px;
                padding: 15px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # متن گزارش
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setAlignment(Qt.AlignRight)
        
        # گزارش نمونه
        sample_report = self.plugin.generate_tahsim_report() if self.plugin else "پلاگین فعال نیست"
        self.report_text.setText(sample_report)
        
        layout.addWidget(self.report_text)
        
        # دکمه بستن
        close_btn = QPushButton("✖ بستن")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


# برای تست مستقل (اگه خواستی جداگانه اجراش کنی)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    plugin = TahsimPlugin()
    print(plugin.get_info())
    
    dialog = TahsimDialog(None, plugin)
    dialog.show()
    
    sys.exit(app.exec_())
