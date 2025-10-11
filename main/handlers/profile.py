from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, CommandHandler  # Add CommandHandler to imports
from main.utils.keyboards import (
    create_main_keyboard, 
    create_back_to_menu_keyboard,
    create_profile_management_keyboard,
    create_registration_cancellation_keyboard,
    create_confirmation_keyboard,
    create_standalone_cancel_keyboard
)
from main.middleware.channel_verify import membership_middleware
from database import db
from main.utils.markdown import escape_markdown, convert_gregorian_to_jalali
import logging
import telegram

logger = logging.getLogger(__name__)

# حالت‌های گفتگو برای انصراف
VIEWING_PROFILE, SELECTING_CANCELLATION, CONFIRMING_CANCELLATION = range(3)

async def show_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پروفایل کاربر با بررسی عضویت در کانال"""
    async def handler(update, context):
        user = update.effective_user
        user_id = user.id
        
        # دریافت اطلاعات کاربر و ثبت‌نام‌ها
        user_registrations = db.get_user_registrations(user_id)
        total_registrations = len(user_registrations)
        
        # ایجاد پیام پروفایل
        profile_message = create_profile_message(user, user_registrations, total_registrations)
        
        # ذخیره اطلاعات کاربر در context برای استفاده بعدی
        context.user_data['user_id'] = user_id
        context.user_data['registrations'] = user_registrations
        
        await update.message.reply_text(
            profile_message,
            reply_markup=create_profile_management_keyboard(total_registrations > 0),
            parse_mode='MarkdownV2'
        )
        
        return VIEWING_PROFILE
    
    return await membership_middleware(update, context, handler, "مشاهده پروفایل")

def safe_unpack_registration(reg_data):
    """Safely unpack registration data with default values."""
    defaults = {
        'reg_id': 0, 'user_id': 0, 'full_name': 'نامشخص', 
        'student_id': 'نامشخص', 'national_id': 'نامشخص',
        'phone_number': 'نامشخص', 'event_name': 'رویداد نامشخص',
        'reg_date': None, 'status': 'active', 
        'notified_admin': False, 'event_type': 'general',
        'event_date': None,
        'event_description': 'توضیحات موجود نیست',
        'event_time': '',
        'event_location': ''
    }
    
    # اگر داده ثبت‌نام شامل همه فیلدها باشد (طول 15)
    if len(reg_data) == 15:
        return dict(zip(list(defaults.keys()), reg_data))
    else:
        result = defaults.copy()
        for i, key in enumerate(defaults.keys()):
            if i < len(reg_data):
                result[key] = reg_data[i]
        return result

def create_profile_message(user, registrations, total_count):
    """ایجاد پیام پروفایل با فرمت مارکداون"""
    # فرار کردن کاراکترهای خاص مارکداون
    first_name = escape_markdown(user.first_name or '')
    last_name = escape_markdown(user.last_name or '')
    username = f"@{escape_markdown(user.username)}" if user.username else "❌ تنظیم نشده"
    
    profile_text = (
        f"👤 *پروفایل کاربر*\n\n"
        f"🆔 *شناسه یکتا:* `{user.id}`\n"
        f"📛 *نام:* {first_name} {last_name}\n"
        f"🔖 *نام کاربری:* {username}\n"
        f"📅 *تعداد رویدادهای ثبت‌نام شده:* {total_count}\n\n"
    )
    
    if total_count > 0:
        profile_text += "🎯 *رویدادهای ثبت‌نام شده:*\n"
        for i, reg_data in enumerate(registrations, 1):
            reg = safe_unpack_registration(reg_data)
            event_name_escaped = escape_markdown(reg['event_name'])
            # نمایش تاریخ برگزاری رویداد به جای تاریخ ثبت‌نام
            event_date = reg.get('event_date') or "نامشخص"
            date_escaped = escape_markdown(event_date)
            profile_text += f"{i}\\. {event_name_escaped} \\(📅 {date_escaped}\\)\n"
        profile_text += "\n⚠️ *توجه:* برای انصراف از ثبت‌نام، از دکمه زیر استفاده کنید\\.\n"
    else:
        profile_text += "📝 *شما هنوز در هیچ رویدادی ثبت‌نام نکرده‌اید*\n\n"
    return profile_text

async def start_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند انصراف از ثبت‌نام"""
    user_id = context.user_data.get('user_id')
    registrations = context.user_data.get('registrations', [])
    
    if not registrations:
        await update.message.reply_text(
            "❌ شما هیچ ثبت‌نام فعالی ندارید\\.",
            reply_markup=create_back_to_menu_keyboard(),
            parse_mode='MarkdownV2'
        )
        return VIEWING_PROFILE
    
    cancellation_message = "📋 *لیست ثبت‌نام‌های فعال:*\n\n"
    
    for i, reg_data in enumerate(registrations, 1):
        reg = safe_unpack_registration(reg_data)
        # تاریخ برگزاری
        event_date = reg.get('event_date') or "نامشخص"
        event_date_escaped = escape_markdown(event_date)
        # توضیحات رویداد
        event_description = escape_markdown(reg.get('event_description', ''))
        # تاریخ ثبت‌نام
        if reg['reg_date']:
            jalali_reg_date = convert_gregorian_to_jalali(reg['reg_date'])
            reg_date_str = escape_markdown(jalali_reg_date)
        else:
            reg_date_str = "نامشخص"
        # شماره تماس
        phone_number_escaped = escape_markdown(reg['phone_number'])
        event_escaped = escape_markdown(reg['event_name'])
        full_name_escaped = escape_markdown(reg['full_name'])
        student_id_escaped = escape_markdown(reg['student_id'])
        cancellation_message += (
            f"{i}\\. *{event_escaped}*\n"
            f"   📅 *تاریخ برگزاری:* {event_date_escaped}\n"
            f"   📝 *توضیحات:* {event_description}\n"
            f"   🗓️ *تاریخ ثبت‌نام:* {reg_date_str}\n"
            f"   👤 *نام:* {full_name_escaped}\n"
            f"   🎫 *شماره دانشجویی:* {student_id_escaped}\n"
            f"   📞 *شماره تماس ثبت‌شده:* {phone_number_escaped}\n\n"
        )
    
    cancellation_message += "❌ برای انصراف از هر رویداد، روی دکمه مربوطه کلیک کنید\\."
    
    await update.message.reply_text(
        cancellation_message,
        reply_markup=create_registration_cancellation_keyboard(registrations),
        parse_mode='MarkdownV2'
    )
    
    return SELECTING_CANCELLATION

async def handle_cancellation_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب ثبت‌نام برای انصراف"""
    query = update.callback_query
    try:
        await query.answer()
    except telegram.error.TimedOut as e:
        logger.warning(f"Timeout answering callback query: {e}")
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")
    
    if query.data == "back_to_profile":
        # بازگشت به پروفایل
        user = update.effective_user
        user_id = user.id
        user_registrations = db.get_user_registrations(user_id)
        total_registrations = len(user_registrations)
        
        profile_message = create_profile_message(user, user_registrations, total_registrations)
        
        await query.edit_message_text(
            text=profile_message,
            parse_mode='MarkdownV2'
        )
        
        # ارسال کیبورد جدید
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="به پروفایل بازگشتید:",
            reply_markup=create_profile_management_keyboard(total_registrations > 0)
        )
        
        return VIEWING_PROFILE
    
    elif query.data.startswith("cancel_reg_"):
        # انتخاب ثبت‌نام برای انصراف
        registration_id = int(query.data.replace("cancel_reg_", ""))
        registration_data = db.get_registration_by_id(registration_id, context.user_data['user_id'])
        
        if not registration_data:
            await query.edit_message_text(
                "❌ ثبت‌نام مورد نظر یافت نشد\\.",
                reply_markup=None,
                parse_mode='MarkdownV2'
            )
            return VIEWING_PROFILE
        
        # ذخیره اطلاعات ثبت‌نام انتخابی
        context.user_data['selected_registration'] = registration_data
        context.user_data['selected_registration_id'] = registration_id
        
        reg = safe_unpack_registration(registration_data)
        
        # استفاده از اطلاعات کامل رویداد
        event_description = escape_markdown(reg.get('event_description', 'توضیحات موجود نیست'))
        event_time = escape_markdown(reg.get('event_time', 'زمان نامشخص'))
        event_location = escape_markdown(reg.get('event_location', 'مکان نامشخص'))
        
        # تاریخ ثبت‌نام
        if reg['reg_date']:
            jalali_date = convert_gregorian_to_jalali(reg['reg_date'])
            date_str = jalali_date
        else:
            date_str = "نامشخص"

        confirmation_message = (
            f"⚠️ *آیا از انصراف از ثبت‌نام زیر مطمئن هستید؟*\n\n"
            f"🎯 *رویداد:* {escape_markdown(reg['event_name'])}\n"
            f"📝 *توضیحات:* {event_description}\n"
            f"⏰ *زمان برگزاری:* {event_time}\n"
            f"📍 *محل برگزاری:* {event_location}\n"
            f"📅 *تاریخ ثبت‌نام:* {escape_markdown(date_str)}\n"
            f"👤 *نام:* {escape_markdown(reg['full_name'])}\n"
            f"🎫 *شماره دانشجویی:* {escape_markdown(reg['student_id'])}\n\n"
            f"❌ *این عمل قابل بازگشت نیست\\!*"
        )
        
        await query.edit_message_text(
            text=confirmation_message,
            reply_markup=create_confirmation_keyboard(registration_id),
            parse_mode='MarkdownV2'
        )
        
        return CONFIRMING_CANCELLATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تأیید انصراف"""
    query = update.callback_query
    try:
        await query.answer()
    except telegram.error.TimedOut as e:
        logger.warning(f"Timeout answering callback query: {e}")
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")
    
    if query.data == "cancel_cancellation":
        # انصراف از انصراف - بازگشت به منوی اصلی
        context.user_data.pop('user_id', None)
        context.user_data.pop('registrations', None)
        context.user_data.pop('selected_registration', None)
        context.user_data.pop('selected_registration_id', None)
        await query.edit_message_text(
            "🏠 به منوی اصلی بازگشتید:",
            reply_markup=None,
            parse_mode='MarkdownV2'
        )
        # Show main menu directly
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 به ربات انجمن علمی مهندسی ساخت و تولید خوش آمدید!\n\n"
                 "🏛 دانشگاه محقق اردبیلی\n\n"
                 "💫 امکانات ربات:\n"
                 "• 📅 مشاهده رویدادها و کارگاه‌ها\n"
                 "• 📝 ثبت‌نام در رویدادها\n"
                 "• 💬 ارتباط با مدیران\n"
                 "• 📞 اطلاعات تماس انجمن",
            reply_markup=create_main_keyboard()
        )
        return ConversationHandler.END
    elif query.data.startswith("confirm_cancel_"):
        # تأیید انصراف و بازگشت به منوی اصلی
        registration_id = int(query.data.replace("confirm_cancel_", ""))
        user_id = context.user_data.get('user_id')
        try:
            db.delete_registration(registration_id, user_id)
            await query.edit_message_text(
                "✅ *انصراف از ثبت‌نام با موفقیت انجام شد\\!*\n\n"
                "🏠 به منوی اصلی بازگشتید:",
                reply_markup=None,
                parse_mode='MarkdownV2'
            )
            # Show main menu directly
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="👋 به ربات انجمن علمی مهندسی ساخت و تولید خوش آمدید!\n\n"
                     "🏛 دانشگاه محقق اردبیلی\n\n"
                     "💫 امکانات ربات:\n"
                     "• 📅 مشاهده رویدادها و کارگاه‌ها\n"
                     "• 📝 ثبت‌نام در رویدادها\n"
                     "• 💬 ارتباط با مدیران\n"
                     "• 📞 اطلاعات تماس انجمن",
                reply_markup=create_main_keyboard()
            )
            context.user_data.pop('user_id', None)
            context.user_data.pop('registrations', None)
            context.user_data.pop('selected_registration', None)
            context.user_data.pop('selected_registration_id', None)
            return ConversationHandler.END
        except Exception as e:
            error_message = f"❌ خطا در انصراف از ثبت‌نام: {escape_markdown(str(e))}"
            await query.edit_message_text(
                text=error_message,
                reply_markup=None,
                parse_mode='MarkdownV2'
            )
            return VIEWING_PROFILE

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    # پاک کردن داده‌های موقت
    context.user_data.pop('user_id', None)
    context.user_data.pop('registrations', None)
    context.user_data.pop('selected_registration', None)
    context.user_data.pop('selected_registration_id', None)
    await update.message.reply_text(
        "🏠 به منوی اصلی بازگشتید:",
        reply_markup=create_main_keyboard()
    )
    return ConversationHandler.END

async def back_to_menu_standalone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی (نسخه مستقل)"""
    # پاک کردن داده‌های موقت
    context.user_data.pop('user_id', None)
    context.user_data.pop('registrations', None)
    context.user_data.pop('selected_registration', None)
    context.user_data.pop('selected_registration_id', None)
    await update.message.reply_text(
        "🏠 به منوی اصلی بازگشتید:",
        reply_markup=create_standalone_cancel_keyboard()
    )
    return ConversationHandler.END

def register_profile_handler(app):
    """ثبت هندلر پروفایل و انصراف"""
    profile_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^👤 مشاهده پروفایل$"), show_user_profile)],
        states={
            VIEWING_PROFILE: [
                MessageHandler(filters.Regex("^❌ انصراف از ثبت‌نام$"), start_cancellation),
                MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), back_to_menu)
            ],
            SELECTING_CANCELLATION: [
                MessageHandler(filters.Regex("^❌ انصراف از ثبت‌نام$"), start_cancellation),
                CallbackQueryHandler(handle_cancellation_selection, pattern="^(cancel_reg_|back_to_profile)")
            ],
            CONFIRMING_CANCELLATION: [
                CallbackQueryHandler(handle_confirmation, pattern="^(confirm_cancel_|cancel_cancellation)")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", back_to_menu_standalone),  # Now CommandHandler is properly imported
            MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), back_to_menu)
        ],
        per_chat=True,
        per_user=True
    )
    
    app.add_handler(profile_conv)
    logger.info("✅ Profile handler with cancellation feature registered successfully")

def register_back_handler(app):
    """ثبت هندلر بازگشت"""
    app.add_handler(MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), back_to_menu_standalone))