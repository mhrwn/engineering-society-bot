from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram import Update, ReplyKeyboardRemove
from main.utils.keyboards import create_cancel_keyboard, create_event_selection_keyboard, create_main_keyboard
from main.utils.validators import validate_full_name, validate_student_id, validate_national_id, validate_phone_number, convert_persian_digits
from main.utils.markdown import escape_markdown
from main.middleware.channel_verify import membership_middleware
from database import db
import logging
import traceback

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_EVENT, ENTERING_NAME, ENTERING_STUDENT_ID, ENTERING_NATIONAL_ID, ENTERING_PHONE = range(5)

async def start_registration(update: Update, context):
    """Start the registration process."""
    async def handler(update, context):
        events = db.get_events()
        if not events:
            await update.message.reply_text(
                "⚠️ در حال حاضر هیچ رویداد یا کارگاهی برای ثبت‌نام موجود نیست.",
                reply_markup=create_main_keyboard()
            )
            return ConversationHandler.END

        await update.message.reply_text(
            "📝 *ثبت‌نام در رویداد*\n\n"
            "⚠️ توجه: هر کاربر تنها یک بار می‌تواند در هر رویداد ثبت‌نام کند\\.\n\n"
            "لطفاً یکی از رویدادهای زیر را انتخاب کنید:",
            reply_markup=create_event_selection_keyboard(events),
            parse_mode='MarkdownV2'
        )
        return SELECTING_EVENT

    return await membership_middleware(update, context, handler, "سیستم ثبت‌نام در رویدادها")

async def handle_event_selection(update: Update, context):
    """Handle event selection."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_registration":
        await cancel_registration(update, context)
        return ConversationHandler.END

    event_name = query.data.replace("event_", "")
    user_id = query.from_user.id

    if db.is_user_registered_for_event(user_id, event_name):
        event_name_escaped = escape_markdown(event_name)
        await query.edit_message_text(
            f"⚠️ شما قبلاً در رویداد '{event_name_escaped}' ثبت‌نام کرده‌اید\\.\n\n"
            f"هر کاربر می‌تواند تنها یک بار در هر رویداد ثبت‌نام کند\\.",
            reply_markup=None,
            parse_mode='MarkdownV2'
        )
        return ConversationHandler.END

    context.user_data['registration'] = {'event': event_name}
    event_name_escaped = escape_markdown(event_name)

    await query.edit_message_text(
        f"✅ *رویداد انتخاب شده: {event_name_escaped}*\n\n"
        f"لطفاً نام و نام خانوادگی خود را وارد کنید:",
        parse_mode='MarkdownV2'
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفاً نام و نام خانوادگی خود را وارد کنید:",
        reply_markup=create_cancel_keyboard()
    )
    return ENTERING_NAME

async def handle_full_name(update: Update, context):
    """Handle full name input."""
    full_name = update.message.text.strip()
    if full_name == "❌ لغو ثبت‌نام":
        await cancel_registration(update, context)
        return ConversationHandler.END

    if not validate_full_name(full_name):
        await update.message.reply_text(
            "⚠️ نام باید حداقل 3 حرف باشد. لطفاً دوباره وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_NAME

    context.user_data['registration']['full_name'] = full_name
    await update.message.reply_text(
        "لطفاً شماره دانشجویی خود را وارد کنید:",
        reply_markup=create_cancel_keyboard()
    )
    return ENTERING_STUDENT_ID


async def handle_student_id(update: Update, context):
    """Handle student ID input."""
    student_id = update.message.text.strip()
    if student_id == "❌ لغو ثبت‌نام":
        await cancel_registration(update, context)
        return ConversationHandler.END

    # Convert Persian digits to English
    student_id_english = convert_persian_digits(student_id)
    
    if not validate_student_id(student_id):
        await update.message.reply_text(
            "⚠️ شماره دانشجویی باید حداقل 8 رقم باشد. لطفاً دوباره وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_STUDENT_ID

    # Store the English version in database
    context.user_data['registration']['student_id'] = student_id_english
    await update.message.reply_text(
        "لطفاً شماره ملی خود را وارد کنید:",
        reply_markup=create_cancel_keyboard()
    )
    return ENTERING_NATIONAL_ID

async def handle_national_id(update: Update, context):
    """Handle national ID input."""
    national_id = update.message.text.strip()
    if national_id == "❌ لغو ثبت‌نام":
        await cancel_registration(update, context)
        return ConversationHandler.END

    # Convert Persian digits to English
    national_id_english = convert_persian_digits(national_id)
    
    if not validate_national_id(national_id):
        await update.message.reply_text(
            "⚠️ شماره ملی باید 10 رقم باشد. لطفاً دوباره وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_NATIONAL_ID

    # Store the English version in database
    context.user_data['registration']['national_id'] = national_id_english
    await update.message.reply_text(
        "لطفاً شماره تماس خود را وارد کنید :",
        reply_markup=create_cancel_keyboard()
    )
    return ENTERING_PHONE

async def handle_phone_number(update: Update, context):
    """Handle phone number input and complete registration."""
    phone_number = update.message.text.strip()
    if phone_number == "❌ لغو ثبت‌نام":
        await cancel_registration(update, context)
        return ConversationHandler.END

    # Convert Persian digits to English
    phone_number_english = convert_persian_digits(phone_number)
    
    if not validate_phone_number(phone_number):
        await update.message.reply_text(
            "⚠️ شماره تماس معتبر نیست. لطفاً شماره را به فرمت 09123456789 وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_PHONE

    registration_data = context.user_data['registration']
    user_id = update.effective_user.id

    try:
        # Use the English version for database storage
        registration_id = db.add_registration(
            user_id=user_id,
            full_name=registration_data['full_name'],
            student_id=registration_data['student_id'],  # Already converted to English
            national_id=registration_data['national_id'],  # Already converted to English
            phone_number=phone_number_english,  # Converted to English
            event_name=registration_data['event']
        )

        # For display, we can show the original or converted version
        full_name_escaped = escape_markdown(registration_data['full_name'])
        student_id_escaped = escape_markdown(registration_data['student_id'])
        national_id_escaped = escape_markdown(registration_data['national_id'])
        phone_escaped = escape_markdown(phone_number_english)
        event_name_escaped = escape_markdown(registration_data['event'])

        success_message = (
            f"🎉 *ثبت‌نام با موفقیت انجام شد\\!*\n\n"
            f"📋 *جزئیات ثبت‌نام:*\n"
            f"• 👤 نام: {full_name_escaped}\n"
            f"• 🎫 شماره دانشجویی: {student_id_escaped}\n"
            f"• 🆔 شماره ملی: {national_id_escaped}\n"
            f"• 📞 شماره تماس: {phone_escaped}\n"
            f"• 🎯 رویداد: {event_name_escaped}\n\n"
            f"🔢 کد پیگیری: \\#{registration_id}\n\n"
            f"با تشکر از ثبت‌نام شما 💫"
        )

        await update.message.reply_text(
            success_message,
            reply_markup=create_main_keyboard(),
            parse_mode='MarkdownV2'
        )
    except ValueError as e:
        error_msg = escape_markdown(str(e))
        await update.message.reply_text(
            f"❌ خطا: {error_msg}",
            reply_markup=create_main_keyboard(),
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await update.message.reply_text(
            "❌ خطا در ثبت‌نام. لطفاً بعداً تلاش کنید.",
            reply_markup=create_main_keyboard()
        )

    context.user_data.pop('registration', None)
    return ConversationHandler.END

async def cancel_registration(update: Update, context):
    """Cancel the registration process."""
    context.user_data.pop('registration', None)
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            "❌ ثبت‌نام لغو شد.",
            reply_markup=create_main_keyboard()
        )
    elif hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("❌ ثبت‌نام لغو شد.")
    return ConversationHandler.END

def register_registration_handler(app):
    """Register registration conversation handler."""
    registration_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 ثبت‌نام در رویداد$"), start_registration)],
        states={
            SELECTING_EVENT: [
                CallbackQueryHandler(handle_event_selection, pattern="^event_"),
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$")
            ],
            ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_full_name)],
            ENTERING_STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_id)],
            ENTERING_NATIONAL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_national_id)],
            ENTERING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
        per_message=False
    )
    app.add_handler(registration_conv)