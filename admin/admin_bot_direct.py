#!/usr/bin/env python3
"""
ربات ادمین - اتصال مستقیم (بدون پروکسی)
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application
from config import Config
from admin.handlers.basic_handlers import setup_basic_handlers
from admin.handlers.reports.report_handlers import setup_report_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """تابع اصلی"""
    if not Config.ADMIN_BOT_TOKEN:
        print("❌ توکن ربات ادمین تنظیم نشده!")
        return
    
    print("🤖 در حال راه‌اندازی ربات ادمین (اتصال مستقیم)...")
    print("⚠️ توجه: استفاده از اتصال مستقیم بدون پروکسی")
    
    try:
        # غیرفعال کردن پروکسی در سطح محیط
        import os
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('ALL_PROXY', None)
        
        # ایجاد application
        application = Application.builder().token(Config.ADMIN_BOT_TOKEN).build()
        
        # تنظیم هندلرها
        setup_basic_handlers(application)
        setup_report_handlers(application)
        
        print("✅ ربات راه‌اندازی شد")
        
        # اجرای ربات
        application.run_polling()
        
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
