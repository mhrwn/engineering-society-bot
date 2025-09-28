from database.manager import DatabaseManager
from config import Config
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdminDatabaseService:
    def __init__(self):
        self.db = DatabaseManager(Config.DATABASE_PATH)
    
    async def get_event_statistics(self):
        """دریافت آمار رویدادها با تطبیق با مدل‌های واقعی"""
        try:
            events = self.db.get_all_events_admin()
            total_events = len(events)
            
            # تطبیق با ساختار tuple برگشتی از manager.py
            active_events = len([e for e in events if isinstance(e, tuple) and len(e) > 7 and e[7]])
            
            # محاسبه کل ثبت‌نام‌ها
            total_registrations = 0
            for e in events:
                if isinstance(e, tuple) and len(e) > 5:
                    total_registrations += e[5]  # registered_count در ایندکس 5
            
            # محاسبه میانگین
            avg_reg = total_registrations / max(total_events, 1)
            
            # ساختاردهی داده‌های رویدادها
            formatted_events = []
            for e in events:
                if isinstance(e, tuple) and len(e) >= 8:
                    formatted_events.append({
                        'id': e[0],  # id
                        'title': e[1],  # name
                        'description': e[2],  # description
                        'date': e[3],  # date
                        'capacity': e[4],  # capacity
                        'registrations_count': e[5],  # registered_count
                        'type': e[6],  # type
                        'is_active': e[7]  # active
                    })
                else:
                    # ساختار fallback برای موارد غیرمنتظره
                    formatted_events.append({
                        'id': 0,
                        'title': 'رویداد نامشخص',
                        'description': '',
                        'date': 'نامشخص',
                        'capacity': 0,
                        'registrations_count': 0,
                        'type': 'event',
                        'is_active': False
                    })
            
            return {
                'total_events': total_events,
                'active_events': active_events,
                'total_registrations': total_registrations,
                'avg_registrations': avg_reg,
                'events': formatted_events
            }
        except Exception as e:
            logger.error(f"خطا در دریافت آمار رویدادها: {e}")
            return None
    
    async def get_user_statistics(self):
        """دریافت آمار کاربران"""
        try:
            # دریافت تمام ثبت‌نام‌ها برای محاسبه کاربران منحصربه‌فرد
            registrations = self.db.get_recent_registrations(1000)  # تعداد زیاد برای آمار دقیق
            
            unique_users = set()
            for reg in registrations:
                if isinstance(reg, tuple) and len(reg) > 1:
                    unique_users.add(reg[1])  # user_id در ایندکس 1
            
            return {
                'total_users': len(unique_users),
                'active_today': min(len(unique_users), 5),  # مقدار نمونه
                'new_this_week': min(len(unique_users), 2)   # مقدار نمونه
            }
        except Exception as e:
            logger.error(f"خطا در دریافت آمار کاربران: {e}")
            return {
                'total_users': 0,
                'active_today': 0,
                'new_this_week': 0
            }
    
    async def get_recent_registrations(self, limit=10):
        """دریافت آخرین ثبت‌نام‌ها"""
        try:
            registrations = self.db.get_recent_registrations(limit)
            formatted_regs = []
            
            for reg in registrations:
                if isinstance(reg, tuple) and len(reg) >= 7:
                    formatted_regs.append({
                        'id': reg[0],  # id
                        'user_id': reg[1],  # user_id
                        'user_name': reg[2],  # full_name
                        'student_id': reg[3],  # student_id
                        'national_id': reg[4],  # national_id
                        'phone_number': reg[5],  # phone_number
                        'event_title': reg[6],  # event_name
                        'registration_date': reg[7].strftime('%Y-%m-%d %H:%M') if len(reg) > 7 and reg[7] else 'نامشخص'
                    })
                else:
                    formatted_regs.append({
                        'id': 0,
                        'user_id': 0,
                        'user_name': 'نامشخص',
                        'student_id': 'نامشخص',
                        'national_id': 'نامشخص',
                        'phone_number': 'نامشخص',
                        'event_title': 'رویداد نامشخص',
                        'registration_date': 'نامشخص'
                    })
            
            return formatted_regs
        except Exception as e:
            logger.error(f"خطا در دریافت ثبت‌نام‌های اخیر: {e}")
            return []
    
    async def get_registrations_by_date_range(self, start_date, end_date):
        """دریافت ثبت‌نام‌ها در بازه زمانی مشخص"""
        try:
            # فعلاً همه ثبت‌نام‌ها را برمی‌گردانیم (فیلتر زمانی بعداً پیاده‌سازی شود)
            return await self.get_recent_registrations(50)
        except Exception as e:
            logger.error(f"خطا در دریافت ثبت‌نام‌ها بر اساس تاریخ: {e}")
            return []
    
    async def get_event_registrations(self, event_id):
        """دریافت لیست ثبت‌نام‌های یک رویداد خاص"""
        try:
            # دریافت نام رویداد بر اساس ID
            events = self.db.get_all_events_admin()
            event_name = None
            for e in events:
                if isinstance(e, tuple) and len(e) > 0 and e[0] == event_id:
                    event_name = e[1]  # نام رویداد در ایندکس 1
                    break
            
            if not event_name:
                return []
            
            # دریافت تمام ثبت‌نام‌ها و فیلتر بر اساس نام رویداد
            all_regs = await self.get_recent_registrations(1000)
            event_regs = [reg for reg in all_regs if reg.get('event_title') == event_name]
            
            return event_regs[:50]  # محدودیت تعداد
        except Exception as e:
            logger.error(f"خطا در دریافت ثبت‌نام‌های رویداد: {e}")
            return []
    
    async def get_unread_messages(self):
        """دریافت پیام‌های خوانده نشده"""
        try:
            # رفع مشکل کوئری پیام‌ها
            messages = self.db.get_all_messages()
            unread_messages = [msg for msg in messages if isinstance(msg, tuple) and len(msg) > 5 and msg[5] == 'unread']
            
            formatted_messages = []
            for msg in unread_messages:
                if isinstance(msg, tuple) and len(msg) >= 6:
                    message_text = msg[3]  # message_text در ایندکس 3
                    formatted_messages.append({
                        'id': msg[0],  # id
                        'user_id': msg[1],  # user_id
                        'user_name': msg[2],  # user_full_name
                        'message_text': message_text[:100] + '...' if len(message_text) > 100 else message_text,
                        'timestamp': msg[4].strftime('%Y-%m-%d %H:%M') if len(msg) > 4 and msg[4] else 'نامشخص',
                        'is_read': False  # چون unread هستند
                    })
            
            return formatted_messages
        except Exception as e:
            logger.error(f"خطا در دریافت پیام‌های خوانده نشده: {e}")
            return []

# نمونه جهانی سرویس
admin_db_service = AdminDatabaseService()
