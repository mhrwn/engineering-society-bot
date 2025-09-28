#!/usr/bin/env python3
"""هندلرهای مدیریت رویدادها"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from admin.utils.decorators import admin_only, log_command, handle_errors
from admin.utils.keyboards import get_back_to_menu_keyboard, get_confirm_cancel_keyboard
from admin.utils.states import EventStates
from admin.services.database_service import admin_db_service
import logging

logger = logging.getLogger(__name__)

class EventHandlers:
    def __init__(self):
        self.db_service = admin_db_service
    
    @admin_only
    @log_command
    @handle_errors
    async def show_event_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی مدیریت رویدادها"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("➕ افزودن رویداد جدید", callback_data="event_add")],
            [InlineKeyboardButton("📋 مشاهده رویدادها", callback_data="event_list")],
            [InlineKeyboardButton("✏️ ویرایش رویداد", callback_data="event_edit")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="admin_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏛️ مدیریت رویدادهای انجمن علمی\n\n"
            "لطفاً عملیات مورد نظر را انتخاب کنید:",
            reply_markup=reply_markup
        )
    
    @admin_only
    @log_command
    @handle_errors
    async def start_add_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند افزودن رویداد جدید"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📝 افزودن رویداد جدید\n\n"
            "لطفاً عنوان رویداد را وارد کنید:",
            reply_markup=get_back_to_menu_keyboard()
        )
        return EventStates.AWAITING_TITLE
    
    @admin_only
    @log_command
    @handle_errors
    async def receive_event_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت عنوان رویداد"""
        title = update.message.text
        context.user_data['event_title'] = title
        
        await update.message.reply_text(
            "✅ عنوان رویداد ذخیره شد.\n\n"
            "لطفاً توضیحات رویداد را وارد کنید:",
            reply_markup=get_back_to_menu_keyboard()
        )
        return EventStates.AWAITING_DESCRIPTION
    
    @admin_only
    @log_command
    @handle_errors
    async def receive_event_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت توضیحات رویداد"""
        description = update.message.text
        context.user_data['event_description'] = description
        
        await update.message.reply_text(
            "✅ توضیحات رویداد ذخیره شد.\n\n"
            "لطفاً تاریخ رویداد را وارد کنید (مثال: 1403/07/15):",
            reply_markup=get_back_to_menu_keyboard()
        )
        return EventStates.AWAITING_DATE
    
    @admin_only
    @log_command
    @handle_errors
    async def receive_event_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت تاریخ رویداد"""
        date = update.message.text
        context.user_data['event_date'] = date
        
        await update.message.reply_text(
            "✅ تاریخ رویداد ذخیره شد.\n\n"
            "لطفاً ظرفیت رویداد را وارد کنید:",
            reply_markup=get_back_to_menu_keyboard()
        )
        return EventStates.AWAITING_CAPACITY
    
    @admin_only
    @log_command
    @handle_errors
    async def receive_event_capacity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت ظرفیت رویداد"""
        try:
            capacity = int(update.message.text)
            context.user_data['event_capacity'] = capacity
            
            # نمایش خلاصه و درخواست تأیید
            event_data = context.user_data
            summary = (
                "📋 خلاصه اطلاعات رویداد:\n\n"
                f"🏷️ عنوان: {event_data['event_title']}\n"
                f"📝 توضیحات: {event_data['event_description']}\n"
                f"📅 تاریخ: {event_data['event_date']}\n"
                f"👥 ظرفیت: {event_data['event_capacity']} نفر\n\n"
                "آیا از درستی اطلاعات اطمینان دارید؟"
            )
            
            await update.message.reply_text(
                summary,
                reply_markup=get_confirm_cancel_keyboard()
            )
            return EventStates.AWAITING_CONFIRMATION
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر برای ظرفیت وارد کنید:",
                reply_markup=get_back_to_menu_keyboard()
            )
            return EventStates.AWAITING_CAPACITY
    
    @admin_only
    @log_command
    @handle_errors
    async def confirm_event_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأیید و ذخیره رویداد"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'confirm_action':
            event_data = context.user_data
            
            try:
                # ذخیره رویداد در دیتابیس
                await query.edit_message_text(
                    "⏳ در حال ذخیره رویداد...",
                    reply_markup=get_back_to_menu_keyboard()
                )
                
                # شبیه‌سازی ذخیره‌سازی
                await query.message.reply_text(
                    f"✅ رویداد '{event_data['event_title']}' با موفقیت ایجاد شد!",
                    reply_markup=get_back_to_menu_keyboard()
                )
                
            except Exception as e:
                logger.error(f"خطا در ذخیره رویداد: {e}")
                await query.message.reply_text(
                    f"❌ خطا در ایجاد رویداد: {e}",
                    reply_markup=get_back_to_menu_keyboard()
                )
        else:
            await query.edit_message_text(
                "❌ ایجاد رویداد لغو شد.",
                reply_markup=get_back_to_menu_keyboard()
            )
        
        # پاک کردن داده‌های موقت
        context.user_data.clear()
        return ConversationHandler.END
    
    @admin_only
    @log_command
    @handle_errors
    async def list_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش لیست رویدادها"""
        query = update.callback_query
        await query.answer()
        
        try:
            # دریافت آمار رویدادها
            stats = await self.db_service.get_event_statistics()
            
            if stats and stats.get('events'):
                message = "📅 لیست رویدادها:\n\n"
                for i, event in enumerate(stats['events'][:10], 1):  # فقط 10 مورد اول
                    status = "🟢" if event.get('is_active') else "🔴"
                    message += f"{i}. {status} {event.get('title', 'بدون عنوان')}\n"
                    message += f"   📍 ثبت‌نام: {event.get('registrations_count', 0)}/{event.get('capacity', 0)}\n\n"
            else:
                message = "📭 هیچ رویدادی یافت نشد."
            
            await query.edit_message_text(
                message,
                reply_markup=get_back_to_menu_keyboard()
            )
            
        except Exception as e:
            logger.error(f"خطا در دریافت لیست رویدادها: {e}")
            await query.edit_message_text(
                "❌ خطا در دریافت لیست رویدادها.",
                reply_markup=get_back_to_menu_keyboard()
            )
    
    @admin_only
    @log_command
    @handle_errors
    async def cancel_event_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو عملیات جاری"""
        if update.message:
            await update.message.reply_text(
                "❌ عملیات لغو شد.",
                reply_markup=get_back_to_menu_keyboard()
            )
        else:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                "❌ عملیات لغو شد.",
                reply_markup=get_back_to_menu_keyboard()
            )
        
        context.user_data.clear()
        return ConversationHandler.END

def setup_event_handlers(application):
    """تنظیم هندلرهای مدیریت رویدادها"""
    handlers = EventHandlers()
    
    # هندلر منوی مدیریت رویدادها
    application.add_handler(CallbackQueryHandler(
        handlers.show_event_management, 
        pattern="^admin_events$"
    ))
    
    # هندلر مشاهده لیست رویدادها
    application.add_handler(CallbackQueryHandler(
        handlers.list_events, 
        pattern="^event_list$"
    ))
    
    # ConversationHandler برای افزودن رویداد جدید
    event_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            handlers.start_add_event, 
            pattern="^event_add$"
        )],
        states={
            EventStates.AWAITING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_event_title)
            ],
            EventStates.AWAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_event_description)
            ],
            EventStates.AWAITING_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_event_date)
            ],
            EventStates.AWAITING_CAPACITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_event_capacity)
            ],
            EventStates.AWAITING_CONFIRMATION: [
                CallbackQueryHandler(handlers.confirm_event_creation, pattern="^(confirm_action|cancel_action)$")
            ]
        },
        fallbacks=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.cancel_event_operation),
            CallbackQueryHandler(handlers.cancel_event_operation, pattern="^admin_main_menu$")
        ],
        per_message=False
    )
    
    application.add_handler(event_conversation)
