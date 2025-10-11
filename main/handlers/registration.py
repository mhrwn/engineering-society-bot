from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from main.utils.keyboards import create_cancel_keyboard, create_event_selection_keyboard, create_main_keyboard
from main.utils.validators import validate_full_name, validate_student_id, validate_national_id, validate_phone_number, convert_persian_digits
from main.utils.markdown import escape_markdown
from main.middleware.channel_verify import membership_middleware
from database import db
import logging
import traceback

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_EVENT, ENTERING_NAME, ENTERING_STUDENT_ID, ENTERING_NATIONAL_ID, ENTERING_PHONE, CONFIRMING_REGISTRATION = range(6)

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

    # 1. Edit the inline keyboard message (no reply_markup, just text)
    await query.edit_message_text(
        f"✅ *رویداد انتخاب شده: {event_name_escaped}*",
        parse_mode='MarkdownV2'
    )
    # 2. Send the prompt as a new message with reply keyboard
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
            "⚠️ نام و نام خانوادگی باید فقط شامل حروف فارسی باشد.\nمثال: علی احمدی",
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
    """Handle phone number input and show registration summary for confirmation."""
    phone_number = update.message.text.strip()
    if phone_number == "❌ لغو ثبت‌نام":
        await cancel_registration(update, context)
        return ConversationHandler.END

    phone_number_english = convert_persian_digits(phone_number)
    
    if not validate_phone_number(phone_number):
        await update.message.reply_text(
            "⚠️ شماره تماس معتبر نیست. لطفاً شماره را به فرمت 09123456789 وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_PHONE

    context.user_data['registration']['phone_number'] = phone_number_english
    # نمایش خلاصه اطلاعات برای تأیید نهایی
    registration_data = context.user_data['registration']
    summary_message = (
        f"📋 *خلاصه اطلاعات ثبت‌نام*\n\n"
        f"👤 *نام:* {escape_markdown(registration_data['full_name'])}\n"
        f"🎫 *شماره دانشجویی:* {escape_markdown(registration_data['student_id'])}\n"
        f"🆔 *شماره ملی:* {escape_markdown(registration_data['national_id'])}\n"
        f"📞 *شماره تماس:* {escape_markdown(registration_data['phone_number'])}\n"
        f"🎯 *رویداد:* {escape_markdown(registration_data['event'])}\n\n"
        f"⚠️ *آیا اطلاعات فوق صحیح است؟*"
    )
    keyboard = [
        [InlineKeyboardButton("✅ تأیید و ثبت نهایی", callback_data="confirm_registration")],
        [InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="edit_registration")],
        [InlineKeyboardButton("❌ لغو ثبت‌نام", callback_data="cancel_registration")]
    ]
    await update.message.reply_text(
        summary_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='MarkdownV2'
    )
    return CONFIRMING_REGISTRATION

async def handle_registration_confirmation(update: Update, context):
    """Handle final confirmation and complete registration."""
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_registration":
        await cancel_registration(update, context)
        return ConversationHandler.END
    elif query.data == "edit_registration":
        await query.edit_message_text(
            "✏️ لطفاً اطلاعات مورد نظر را ویرایش کنید و مجدداً ثبت نمایید.",
            reply_markup=None
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً نام و نام خانوادگی خود را وارد کنید:",
            reply_markup=create_cancel_keyboard()
        )
        return ENTERING_NAME
    elif query.data == "confirm_registration":
        registration_data = context.user_data['registration']
        user_id = update.effective_user.id
        try:
            registration_id = db.add_registration(
                user_id=user_id,
                full_name=registration_data['full_name'],
                student_id=registration_data['student_id'],
                national_id=registration_data['national_id'],
                phone_number=registration_data['phone_number'],
                event_name=registration_data['event']
            )
            full_name_escaped = escape_markdown(registration_data['full_name'])
            student_id_escaped = escape_markdown(registration_data['student_id'])
            national_id_escaped = escape_markdown(registration_data['national_id'])
            phone_escaped = escape_markdown(registration_data['phone_number'])
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
            # Only edit the message text, do NOT send reply_markup here
            await query.edit_message_text(
                success_message,
                parse_mode='MarkdownV2'
            )
            # Send main menu as a new message with reply keyboard
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🏠 به منوی اصلی بازگشتید:",
                reply_markup=create_main_keyboard()
            )
        except ValueError as e:
            error_msg = escape_markdown(str(e))
            await query.edit_message_text(
                f"❌ خطا: {error_msg}",
                parse_mode='MarkdownV2'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🏠 به منوی اصلی بازگشتید:",
                reply_markup=create_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Registration error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            await query.edit_message_text(
                "❌ خطا در ثبت‌نام. لطفاً بعداً تلاش کنید.",
                parse_mode='MarkdownV2'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🏠 به منوی اصلی بازگشتید:",
                reply_markup=create_main_keyboard()
            )
        context.user_data.pop('registration', None)
        return ConversationHandler.END

async def cancel_registration(update: Update, context):
    """Cancel the registration process and return to main menu."""
    context.user_data.pop('registration', None)
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            "❌ ثبت‌نام لغو شد.",
            reply_markup=create_main_keyboard()
        )
    elif hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "❌ ثبت‌نام لغو شد.",
            reply_markup=None
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏠 به منوی اصلی بازگشتید:",
            reply_markup=create_main_keyboard()
        )
    return ConversationHandler.END

def register_registration_handler(app):
    """Register registration conversation handler."""
    registration_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 ثبت‌نام در کارگاه‌ها و رویدادها$"), start_registration)],
        states={
            SELECTING_EVENT: [
                CallbackQueryHandler(handle_event_selection, pattern="^event_"),
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$")
            ],
            ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_full_name)],
            ENTERING_STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_id)],
            ENTERING_NATIONAL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_national_id)],
            ENTERING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number)],
            CONFIRMING_REGISTRATION: [
                CallbackQueryHandler(handle_registration_confirmation, pattern="^(confirm_registration|edit_registration|cancel_registration)$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_registration),  # Add explicit command handler
            MessageHandler(filters.Regex("^❌ لغو ثبت‌نام$"), cancel_registration)
        ],
        per_message=False
    )
    app.add_handler(registration_conv)