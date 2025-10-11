import logging
from telegram.error import BadRequest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from main.utils.keyboards import create_main_keyboard  # Added missing import
from config import Config
from collections import defaultdict
from datetime import datetime, timedelta
from main.utils.markdown import escape_markdown
from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)

async def check_channel_membership(user_id, bot):
    """Check if user is a member of the specified channel."""
    try:
        member = await bot.get_chat_member(chat_id=Config.CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest as e:
        logger.error(f"Error checking channel membership: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking channel membership: {e}")
        return False

def create_membership_keyboard():
    """Create inline keyboard for channel membership verification."""
    # Remove escape_markdown from URL - this was causing the issue
    keyboard = [
        [InlineKeyboardButton("✨ عضویت در کانال", url=Config.CHANNEL_URL)],
        [InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_membership_required_message(update, context, feature_name):
    """Send a message requiring channel membership with a glass-like keyboard."""
    escaped_feature = escape_markdown(feature_name.replace('_', ' '))
    # Do NOT escape the entire message, only variables
    beautiful_message = (
        f"🌟 *دسترسی ویژه* 🌟\n\n"
        f"برای استفاده از {escaped_feature}، لطفاً در کانال انجمن عضو شوید.\n\n"
        f"📢 *مزایای عضویت:*\n"
        f"• 🔥 دسترسی به آخرین رویدادها\n"
        f"• 💫 امکان ثبت‌نام در کارگاه‌ها\n"
        f"• ✨ ارتباط مستقیم با مدیران\n"
        f"• 🎯 اطلاع‌رسانی فوری\n\n"
        f"پس از عضویت، روی *✅ تایید عضویت* کلیک کنید."
    )

    beautiful_message = escape_markdown(beautiful_message)

    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            beautiful_message,
            reply_markup=create_membership_keyboard(),
            parse_mode='MarkdownV2'
        )
    elif hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            beautiful_message,
            reply_markup=create_membership_keyboard(),
            parse_mode='MarkdownV2'
        )

class RateLimiter:
    def __init__(self):
        self.user_attempts = defaultdict(list)
    def is_rate_limited(self, user_id, action, max_attempts=5, window_minutes=10):
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        self.user_attempts[user_id] = [
            attempt_time for attempt_time in self.user_attempts[user_id]
            if attempt_time > window_start
        ]
        if len(self.user_attempts[user_id]) >= max_attempts:
            return True
        self.user_attempts[user_id].append(now)
        return False

rate_limiter = RateLimiter()

async def membership_middleware(update, context, handler, feature_name):
    """Middleware to enforce channel membership before executing handler."""
    user_id = update.effective_user.id
    # اضافه کردن rate limiting
    if rate_limiter.is_rate_limited(user_id, "channel_check", max_attempts=5, window_minutes=10):
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "⏳ لطفاً بعداً تلاش کنید. محدودیت بررسی عضویت فعال شده است.",
                parse_mode='MarkdownV2'
            )
        elif hasattr(update, 'callback_query') and update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                "⏳ لطفاً بعداً تلاش کنید. محدودیت بررسی عضویت فعال شده است.",
                parse_mode='MarkdownV2'
            )
        return None
    is_member = await check_channel_membership(user_id, context.bot)
    if not is_member:
        await send_membership_required_message(update, context, feature_name)
        return None
    return await handler(update, context)

def register_middleware_handlers(app):
    """Register middleware handlers for channel membership checks."""
    app.add_handler(CommandHandler("cancel", lambda u, c: u.message.reply_text(  # Simple cancel handler
        "❌ عملیات لغو شد.",
        reply_markup=create_main_keyboard()
    )))
