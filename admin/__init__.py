"""
ربات ادمین برای مدیریت انجمن علمی مهندسی ساخت و تولید
"""

__version__ = "1.0.0"
__author__ = "انجمن علمی مهندسی ساخت و تولید"

# ایمپورت‌های سرویس‌ها
from .services.database_service import AdminDatabaseService

# ایمپورت توابع اصلی از admin_bot
from .admin_bot import main

# برای سازگاری با کدهای قدیمی - تعریف یک کلاس dummy برای AdminBot
class AdminBot:
    """کلاس dummy برای سازگاری با ایمپورت‌های قدیمی"""
    pass

# ایمپورت هندلرها برای دسترسی آسان
from .handlers.basic_handlers import setup_basic_handlers
from .handlers.reports.report_handlers import setup_report_handlers

__all__ = [
    'AdminBot',
    'AdminDatabaseService', 
    'main',
    'setup_basic_handlers',
    'setup_report_handlers'
]
