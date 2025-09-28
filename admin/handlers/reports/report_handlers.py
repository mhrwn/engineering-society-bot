from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from admin.utils.decorators import admin_only, log_command, handle_errors
from admin.utils.keyboards import (
    get_report_types_keyboard, 
    get_back_to_menu_keyboard,
    get_date_range_keyboard,
    get_confirm_cancel_keyboard
)
from admin.utils.states import ReportStates
from admin.services.database_service import admin_db_service
import os
import logging

logger = logging.getLogger(__name__)

class ReportHandlers:
    def __init__(self):
        self.db_service = admin_db_service
        self.temp_data = {}
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_report_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب نوع گزارش"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📊 لطفا نوع گزارش مورد نظر را انتخاب کنید:",
            reply_markup=get_report_types_keyboard()
        )
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_registration_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """گزارش ثبت‌نام‌ها"""
        query = update.callback_query
        await query.answer()
        
        # دریافت آخرین ثبت‌نام‌ها
        registrations = await self.db_service.get_recent_registrations(10)
        
        if registrations:
            report_text = "📋 آخرین ثبت‌نام‌ها:\n\n"
            for reg in registrations:
                report_text += f"• {reg['user_name']} - {reg['event_title']}\n"
        else:
            report_text = "📭 هیچ ثبت‌نامی یافت نشد."
        
        await query.edit_message_text(
            report_text,
            reply_markup=get_back_to_menu_keyboard()
        )
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_user_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار کاربران"""
        query = update.callback_query
        await query.answer()
        
        stats = await self.db_service.get_user_statistics()
        
        if stats:
            message = (
                "👥 آمار کاربران:\n\n"
                f"• تعداد کل کاربران: {stats['total_users']}\n"
                f"• کاربران فعال امروز: {stats['active_today']}\n"
                f"• کاربران جدید این هفته: {stats['new_this_week']}"
            )
        else:
            message = "❌ خطا در دریافت آمار کاربران"
        
        await query.edit_message_text(
            message,
            reply_markup=get_back_to_menu_keyboard()
        )
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_general_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار کلی سیستم"""
        query = update.callback_query
        await query.answer()
        
        stats = await self.db_service.get_event_statistics()
        
        if stats:
            message = (
                "📈 آمار کلی سیستم:\n\n"
                f"• تعداد کل رویدادها: {stats['total_events']}\n"
                f"• رویدادهای فعال: {stats['active_events']}\n"
                f"• کل ثبت‌نام‌ها: {stats['total_registrations']}\n"
                f"• میانگین ثبت‌نام per رویداد: {stats['avg_registrations']:.1f}"
            )
        else:
            message = "❌ خطا در دریافت آمار سیستم"
        
        await query.edit_message_text(
            message,
            reply_markup=get_back_to_menu_keyboard()
        )
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_pdf_report_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """درخواست تولید گزارش PDF"""
        query = update.callback_query
        await query.answer()
        
        # ذخیره نوع گزارش در context
        context.user_data['report_type'] = 'events'
        
        await query.edit_message_text(
            "📄 لطفا بازه زمانی گزارش را انتخاب کنید:",
            reply_markup=get_date_range_keyboard()
        )
        return ReportStates.AWAITING_DATE_RANGE
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_date_range_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """انتخاب بازه زمانی"""
        query = update.callback_query
        await query.answer()
        
        date_range = query.data.replace('date_range_', '')
        context.user_data['date_range'] = date_range
        
        await query.edit_message_text(
            f"✅ بازه زمانی '{date_range}' انتخاب شد.\n"
            "آیا مایل به تولید گزارش PDF هستید؟",
            reply_markup=get_confirm_cancel_keyboard()
        )
        return ReportStates.AWAITING_CONFIRMATION
    
    @admin_only
    @log_command
    @handle_errors
    async def handle_pdf_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تولید گزارش PDF"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'confirm_action':
            await query.edit_message_text("⏳ در حال تولید گزارش PDF...")
            
            try:
                # دریافت داده‌ها
                events_data = await self.db_service.get_event_statistics()
                
                # تولید گزارش ساده (بدون PDF برای حالا)
                if events_data:
                    report_text = "📊 گزارش آماری:\n\n"
                    report_text += f"تعداد رویدادها: {events_data['total_events']}\n"
                    report_text += f"رویدادهای فعال: {events_data['active_events']}\n"
                    report_text += f"کل ثبت‌نام‌ها: {events_data['total_registrations']}\n"
                    report_text += f"میانگین ثبت‌نام: {events_data['avg_registrations']:.1f}"
                    
                    await query.message.reply_text(
                        report_text,
                        reply_markup=get_back_to_menu_keyboard()
                    )
                else:
                    await query.message.reply_text(
                        "❌ داده‌ای برای گزارش یافت نشد.",
                        reply_markup=get_back_to_menu_keyboard()
                    )
                    
            except Exception as e:
                logger.error(f"خطا در تولید گزارش: {e}")
                await query.message.reply_text(
                    f"❌ خطا در تولید گزارش: {e}",
                    reply_markup=get_back_to_menu_keyboard()
                )
        else:
            await query.edit_message_text(
                "❌ تولید گزارش لغو شد.",
                reply_markup=get_back_to_menu_keyboard()
            )
        
        return ConversationHandler.END
    
    @admin_only
    @log_command
    @handle_errors
    async def cancel_report_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو تولید گزارش"""
        await update.message.reply_text(
            "❌ تولید گزارش لغو شد.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return ConversationHandler.END

# تابع برای تنظیم هندلرها
def setup_report_handlers(application):
    """تنظیم هندلرهای گزارش‌گیری"""
    handlers = ReportHandlers()
    
    # هندلرهای اصلی گزارش‌ها
    application.add_handler(CallbackQueryHandler(handlers.handle_report_selection, pattern="^admin_reports$"))
    application.add_handler(CallbackQueryHandler(handlers.handle_registration_report, pattern="^report_registrations$"))
    application.add_handler(CallbackQueryHandler(handlers.handle_user_statistics, pattern="^report_users$"))
    application.add_handler(CallbackQueryHandler(handlers.handle_general_statistics, pattern="^report_stats$"))
    application.add_handler(CallbackQueryHandler(handlers.handle_pdf_report_request, pattern="^report_pdf$"))
    
    # هندلر تولید PDF (مکالمه‌ای)
    pdf_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.handle_pdf_report_request, pattern="^report_pdf$")],
        states={
            ReportStates.AWAITING_DATE_RANGE: [
                CallbackQueryHandler(handlers.handle_date_range_selection, pattern="^date_range_")
            ],
            ReportStates.AWAITING_CONFIRMATION: [
                CallbackQueryHandler(handlers.handle_pdf_generation, pattern="^(confirm_action|cancel_action)$")
            ]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.cancel_report_generation)],
        per_message=False
    )
    
    application.add_handler(pdf_conversation)
