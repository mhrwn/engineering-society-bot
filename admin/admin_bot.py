#!/usr/bin/env python3
"""
ربات ادمین - نسخه اصلی با پشتیبانی از ماژول‌های مدیریتی
"""

import sys
import os
import logging
import socks
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application
from config import Config
from admin.handlers.basic_handlers import setup_basic_handlers
from admin.handlers.reports.report_handlers import setup_report_handlers
from admin.handlers.events.event_handlers import setup_event_handlers

# تنظیم پروکسی مانند ربات اصلی
if Config.PROXY_URL and Config.PROXY_URL.startswith("socks5://"):
    try:
        proxy_url = Config.PROXY_URL.replace("socks5://", "")
        host, port = proxy_url.split(":")
        socks.set_default_proxy(socks.SOCKS5, host, int(port))
        socket.socket = socks.socksocket
        logging.info(f"🔗 پروکسی تنظیم شد: {host}:{port}")
    except Exception as e:
        logging.error(f"❌ خطا در تنظیم پروکسی: {e}")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """تابع اصلی"""
    if not Config.ADMIN_BOT_TOKEN:
        print("❌ توکن ربات ادمین تنظیم نشده!")
        return
    
    try:
        print("🤖 در حال راه‌اندازی ربات ادمین...")
        
        application = Application.builder().token(Config.ADMIN_BOT_TOKEN).build()
        
        # تنظیم هندلرها
        setup_basic_handlers(application)
        setup_report_handlers(application)
        setup_event_handlers(application)  # اضافه شدن مدیریت رویدادها
        
        print("✅ ربات راه‌اندازی شد")
        print("📊 ماژول‌های فعال: پایه, گزارش‌ها, رویدادها")
        print("🤖 ربات ادمین در حال اجرا است...")
        
        application.run_polling()
        
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
