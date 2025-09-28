#!/usr/bin/env python3
"""
ربات ادمین - نسخه نهایی با رفع مشکل event loop
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

# تنظیم پروکسی دقیقاً مانند ربات اصلی
def setup_proxy():
    """تنظیم پروکسی مانند ربات اصلی"""
    proxy_url = Config.PROXY_URL
    if proxy_url and proxy_url.startswith("socks5://"):
        try:
            proxy_url = proxy_url.replace("socks5://", "")
            host, port = proxy_url.split(":")
            socks.set_default_proxy(socks.SOCKS5, host, int(port))
            socket.socket = socks.socksocket
            logging.info(f"🔗 پروکسی تنظیم شد: {host}:{port}")
            return True
        except Exception as e:
            logging.error(f"❌ خطا در تنظیم پروکسی: {e}")
            return False
    return False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """تابع اصلی"""
    if not Config.ADMIN_BOT_TOKEN:
        print("❌ توکن ربات ادمین تنظیم نشده!")
        return
    
    print("🤖 در حال راه‌اندازی ربات ادمین...")
    
    # تنظیم پروکسی
    proxy_status = setup_proxy()
    if not proxy_status:
        print("⚠️ پروکسی تنظیم نشد - تلاش برای اتصال مستقیم")
    
    try:
        # ایجاد application
        application = Application.builder().token(Config.ADMIN_BOT_TOKEN).build()
        
        # تنظیم هندلرها
        setup_basic_handlers(application)
        setup_report_handlers(application)
        
        print("✅ ربات راه‌اندازی شد")
        print("🤖 ربات ادمین در حال اجرا است...")
        print("📱 برای خروج از Ctrl+C استفاده کنید")
        
        # اجرای ربات - بدون تست اتصال جداگانه
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
