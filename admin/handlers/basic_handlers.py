#!/usr/bin/env python3
"""هندلرهای پایه ربات ادمین"""

from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from admin.utils.decorators import admin_only, log_command
from admin.utils.keyboards import get_admin_main_menu, get_back_to_menu_keyboard
from admin.utils.states import AdminStates
from admin.services.database_service import admin_db_service

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع برای ادمین"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n"
        f"به پنل مدیریت انجمن علمی خوش آمدید.\n\n"
        f"🏛️ انجمن علمی مهندسی ساخت و تولید\n"
        f"🎓 دانشگاه محقق اردبیلی",
        reply_markup=get_admin_main_menu()
    )
    return AdminStates.MAIN_MENU

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "منوی اصلی مدیریت:",
        reply_markup=get_admin_main_menu()
    )
    return AdminStates.MAIN_MENU

async def show_reports_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش بخش گزارش‌ها"""
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار
    stats = await admin_db_service.get_event_statistics()
    if stats:
        message = (
            "📊 آمار کلی سیستم:\n\n"
            f"• تعداد کل رویدادها: {stats['total_events']}\n"
            f"• رویدادهای فعال: {stats['active_events']}\n"
            f"• کل ثبت‌نام‌ها: {stats['total_registrations']}\n"
            f"• میانگین ثبت‌نام per رویداد: {stats['avg_registrations']:.1f}\n\n"
            "لطفا نوع گزارش مورد نظر را انتخاب کنید:"
        )
    else:
        message = "❌ خطا در دریافت آمار سیستم"
    
    from admin.utils.keyboards import get_report_types_keyboard
    await query.edit_message_text(
        message,
        reply_markup=get_report_types_keyboard()
    )

async def exit_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خروج از حالت ادمین"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ از حالت مدیریت خارج شدید.")
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات جاری"""
    await update.message.reply_text(
        "❌ عملیات لغو شد.",
        reply_markup=get_admin_main_menu()
    )
    return AdminStates.MAIN_MENU

# هندلر برای پیام‌های متنی (اگر کاربر مستقیماً متن وارد کند)
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    text = update.message.text
    if text == "منوی اصلی":
        await update.message.reply_text(
            "منوی اصلی مدیریت:",
            reply_markup=get_admin_main_menu()
        )
        return AdminStates.MAIN_MENU
    else:
        await update.message.reply_text(
            "⚠️ لطفاً از دکمه‌های منو استفاده کنید.",
            reply_markup=get_admin_main_menu()
        )
        return AdminStates.MAIN_MENU

def setup_basic_handlers(application):
    """تنظیم هندلرهای پایه"""
    # ConversationHandler برای مدیریت حالت‌ها
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            AdminStates.MAIN_MENU: [
                CallbackQueryHandler(main_menu_callback, pattern="^admin_main_menu$"),
                CallbackQueryHandler(show_reports_callback, pattern="^admin_reports$"),
                CallbackQueryHandler(exit_admin_callback, pattern="^admin_exit$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("start", start_command)
        ],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    
    # هندلرهای اضافی برای دستورات مستقل
    application.add_handler(CommandHandler("cancel", cancel_command))
