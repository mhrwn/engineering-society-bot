#!/usr/bin/env python3
"""دکوراتورهای امنیتی و لاگینگ برای ربات ادمین"""

from functools import wraps
from config import Config
import logging

logger = logging.getLogger(__name__)

def admin_only(func):
    """دکوراتور برای محدود کردن دسترسی به ادمین‌ها"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            # بررسی اینکه آیا update دارای effective_user است یا خیر
            if hasattr(update, 'effective_user'):
                user_id = update.effective_user.id
            elif hasattr(update, 'message') and update.message:
                user_id = update.message.from_user.id
            elif hasattr(update, 'callback_query') and update.callback_query:
                user_id = update.callback_query.from_user.id
            else:
                # اگر نتوانستیم user_id را پیدا کنیم، اجازه دسترسی ندهیم
                await update.answer("❌ دسترسی غیرمجاز", show_alert=True)
                return
            
            # بررسی دسترسی ادمین
            if user_id not in Config.ADMIN_CHAT_IDS:
                if hasattr(update, 'answer'):
                    await update.answer("❌ شما دسترسی ادمین ندارید", show_alert=True)
                elif hasattr(update, 'message') and update.message:
                    await update.message.reply_text("❌ شما دسترسی ادمین ندارید")
                return
            
            # اجرای تابع اصلی
            return await func(update, context, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"خطا در دکوراتور admin_only: {e}")
            if hasattr(update, 'answer'):
                await update.answer("❌ خطا در بررسی دسترسی", show_alert=True)
    
    return wrapper

def log_command(func):
    """دکوراتور برای لاگینگ دستورات"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            # استخراج اطلاعات کاربر
            if hasattr(update, 'effective_user'):
                user_info = f"{update.effective_user.first_name} (ID: {update.effective_user.id})"
            elif hasattr(update, 'callback_query') and update.callback_query:
                user_info = f"{update.callback_query.from_user.first_name} (ID: {update.callback_query.from_user.id})"
            else:
                user_info = "نامشخص"
            
            # استخراج نوع دستور
            if hasattr(update, 'callback_query') and update.callback_query:
                command = f"callback: {update.callback_query.data}"
            elif hasattr(update, 'message') and update.message and update.message.text:
                command = f"command: {update.message.text}"
            else:
                command = "unknown"
            
            logger.info(f"🔹 دستور از {user_info} - {command}")
            
            # اجرای تابع اصلی
            result = await func(update, context, *args, **kwargs)
            
            logger.info(f"✅ دستور تکمیل شد - {command}")
            return result
            
        except Exception as e:
            logger.error(f"❌ خطا در اجرای دستور: {e}")
            raise
    
    return wrapper

def handle_errors(func):
    """دکوراتور برای مدیریت خطاها"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"❌ خطا در هندلر {func.__name__}: {e}")
            
            # ارسال پیام خطا به کاربر
            try:
                if hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.answer("❌ خطا در پردازش درخواست", show_alert=True)
                elif hasattr(update, 'message') and update.message:
                    await update.message.reply_text("❌ خطا در پردازش درخواست")
            except Exception:
                pass
            
            return None
    
    return wrapper
