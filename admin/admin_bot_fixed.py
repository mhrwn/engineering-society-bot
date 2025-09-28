#!/usr/bin/env python3
"""
ربات ادمین - با روش پروکسی مشابه ربات اصلی
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
        print("🔗 در حال اتصال به تلگرام...")
        
        # تست اتصال
        import asyncio
        async def test_connection():
            bot = application.bot
            try:
                me = await bot.get_me()
                print(f"✅ اتصال موفق - ربات: {me.first_name} (@{me.username})")
                return True
            except Exception as e:
                print(f"❌ خطا در اتصال: {e}")
                return False
        
        # تست اتصال قبل از اجرای ربات
        connection_ok = asyncio.run(test_connection())
        if not connection_ok:
            print("❌ عدم توانایی در اتصال به تلگرام")
            print("⚠️ لطفاً پروکسی را بررسی کنید")
            return
        
        print("🤖 ربات ادمین در حال اجرا است...")
        print("📱 برای خروج از Ctrl+C استفاده کنید")
        
        # اجرای ربات
        application.run_polling()
        
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
