from telegram.ext import ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from telegram import Update, ReplyKeyboardRemove
from main.utils.validators import validate_message_text
from main.utils.markdown import escape_markdown
from main.utils.keyboards import create_main_keyboard
from main.middleware.channel_verify import membership_middleware
from database import db
from config import Config
import logging
import traceback

logger = logging.getLogger(__name__)

# Conversation states
ENTERING_MESSAGE = 0

async def start_contact(update: Update, context):
    """Start the contact process with daily message limit and channel membership check."""
    async def handler(update, context):
        user_id = update.effective_user.id
        try:
            messages_today = db.get_user_messages_today(user_id)
            if messages_today >= Config.MAX_MESSAGES_PER_DAY:
                await update.message.reply_text(
                    f"⚠️ *شما امروز {messages_today} پیام ارسال کرده‌اید\\.*\n"
                    f"لطفاً فردا مجدداً تلاش کنید\\.\n\n"
                    f"با تشکر از صبر و شکیبایی شما 🙏",
                    reply_markup=create_main_keyboard(),
                    parse_mode='MarkdownV2'
                )
                return ConversationHandler.END

            await update.message.reply_text(
                "💬 *تماس با مدیر*\n\n"
                f"لطفاً پیام خود را برای مدیران انجمن ارسال کنید\\.\n"
                f"⚠️ توجه: هر کاربر تنها می‌تواند {Config.MAX_MESSAGES_PER_DAY} پیام در روز ارسال کند\\.\n\n"
                f"پیام شما در اسرع وقت بررسی و پاسخ داده خواهد شد\\.\n\n"
                f"برای لغو دستور /cancel را وارد کنید\\.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='MarkdownV2'
            )
            return ENTERING_MESSAGE
        except Exception as e:
            logger.error(f"Error in start_contact: {e}")
            await update.message.reply_text(
                "❌ خطا در سیستم. لطفاً بعداً تلاش کنید.",
                reply_markup=create_main_keyboard()
            )
            return ConversationHandler.END

    return await membership_middleware(update, context, handler, "سیستم تماس با مدیر")

async def handle_user_message(update: Update, context):
    """Handle and store user message."""
    try:
        message_text = update.message.text
        if not validate_message_text(message_text):
            await update.message.reply_text(
                "⚠️ پیام باید حداقل 5 حرف باشد. لطفاً پیام معتبرتری ارسال کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            return ENTERING_MESSAGE

        user_id = update.effective_user.id
        messages_today = db.get_user_messages_today(user_id)
        if messages_today >= Config.MAX_MESSAGES_PER_DAY:
            await update.message.reply_text(
                f"⚠️ شما امروز {messages_today} پیام ارسال کرده‌اید.\n"
                f"لطفاً فردا مجدداً تلاش کنید.",
                reply_markup=create_main_keyboard()
            )
            return ConversationHandler.END

        user = update.effective_user
        message_id = db.add_user_message(
            user_id=user.id,
            user_full_name=user.full_name,
            message_text=message_text
        )

        message_text_escaped = escape_markdown(message_text)
        await update.message.reply_text(
            f"✅ *پیام شما با موفقیت ارسال شد\\!*\n\n"
            f"📋 کد پیگیری: \\#{message_id}\n"
            f"📝 پیام شما: {message_text_escaped}\n\n"
            f"با تشکر از ارتباط شما 🙏",
            reply_markup=create_main_keyboard(),
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await update.message.reply_text(
            "❌ خطا در ارسال پیام. لطفاً بعداً تلاش کنید.",
            reply_markup=create_main_keyboard()
        )
    return ConversationHandler.END

async def cancel_contact(update: Update, context):
    """Cancel the contact process."""
    await update.message.reply_text(
        "❌ ارسال پیام لغو شد.",
        reply_markup=create_main_keyboard()
    )
    return ConversationHandler.END

async def check_membership_callback(update: Update, context):
    """Handle membership verification callback."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    is_member = await context.bot.get_chat_member(chat_id=Config.CHANNEL_ID, user_id=user_id)
    is_member = is_member.status in ['member', 'administrator', 'creator']

    if is_member:
        # Remove the inline keyboard completely for the success message
        await query.edit_message_text(
            "🎉 *تبریک\\! عضویت شما تایید شد\\!*\n\n"
            "اکنون می‌توانید از تمام امکانات ربات استفاده کنید\\.\n\n"
            "لطفاً از منوی زیر انتخاب کنید:",
            reply_markup=None,
            parse_mode='MarkdownV2'
        )
    else:
        from main.middleware.channel_verify import create_membership_keyboard
        await query.edit_message_text(
            "❌ *متأسفانه هنوز در کانال عضو نیستید\\.*\n\n"
            "لطفاً مراحل زیر را انجام دهید:\n"
            "1\\. روی دکمه '✨ عضویت در کانال' کلیک کنید\n"
            "2\\. در کانال عضو شوید\n"
            "3\\. سپس روی '✅ تایید عضویت' کلیک کنید\n\n"
            "پس از عضویت، امکانات ویژه ربات برای شما فعال خواهد شد\\.",
            reply_markup=create_membership_keyboard(),
            parse_mode='MarkdownV2'
        )

def register_messaging_handler(app):
    """Register messaging conversation handler."""
    contact_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💬 تماس با مدیر$"), start_contact)],
        states={
            ENTERING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel_contact)],
        per_message=False
    )
    app.add_handler(contact_conv)
    app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="^check_membership$"))