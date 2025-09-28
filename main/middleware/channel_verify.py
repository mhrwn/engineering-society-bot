import logging
from telegram.error import BadRequest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

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
    keyboard = [
        [InlineKeyboardButton("✨ عضویت در کانال", url=Config.CHANNEL_URL)],
        [InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_membership_required_message(update, context, feature_name):
    """Send a message requiring channel membership with a glass-like keyboard."""
    escaped_feature = feature_name.replace('_', '\\_')
    beautiful_message = (
        f"🌟 *دسترسی ویژه* 🌟\n\n"
        f"برای استفاده از {escaped_feature}، لطفاً در کانال انجمن عضو شوید\\.\n\n"
        f"📢 *مزایای عضویت:*\n"
        f"• 🔥 دسترسی به آخرین رویدادها\n"
        f"• 💫 امکان ثبت‌نام در کارگاه‌ها\n"
        f"• ✨ ارتباط مستقیم با مدیران\n"
        f"• 🎯 اطلاع‌رسانی فوری\n\n"
        f"پس از عضویت، روی *✅ تایید عضویت* کلیک کنید\\."
    )

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

async def membership_middleware(update, context, handler, feature_name):
    """Middleware to enforce channel membership before executing handler."""
    user_id = update.effective_user.id
    is_member = await check_channel_membership(user_id, context.bot)
    
    if not is_member:
        await send_membership_required_message(update, context, feature_name)
        return None
    return await handler(update, context)
