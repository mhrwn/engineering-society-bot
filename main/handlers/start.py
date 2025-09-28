from telegram.ext import CommandHandler
from telegram import Update
from main.utils.keyboards import create_main_keyboard
from main.utils.markdown import escape_markdown
from config import Config
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context):
    """Handle /start command."""
    user_id = update.effective_user.id
    is_member = await context.bot.get_chat_member(chat_id=Config.CHANNEL_ID, user_id=user_id)
    is_member = is_member.status in ['member', 'administrator', 'creator']

    society_name_escaped = escape_markdown(Config.SOCIETY_NAME)
    university_escaped = escape_markdown(Config.UNIVERSITY)
    channel_url_escaped = escape_markdown(Config.CHANNEL_URL)

    welcome_text = (
        f"👋 *به ربات {society_name_escaped} خوش آمدید\\!*\n\n"
        f"🏛 {university_escaped}\n\n"
        "💫 *امکانات ربات:*\n"
        "• 📅 مشاهده رویدادها و کارگاه‌ها\n"
        "• 📝 ثبت‌نام در رویدادها\n"
        "• 💬 ارتباط با مدیران\n"
        "• 📞 اطلاعات تماس انجمن\n\n"
    )

    if not is_member:
        welcome_text += (
            f"🌟 *برای دسترسی به تمام امکانات، در کانال ما عضو شوید:*\n"
            f"{channel_url_escaped}"
        )

    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_keyboard(),
        parse_mode='MarkdownV2'
    )

def register_start_handler(app):
    """Register start command handler."""
    app.add_handler(CommandHandler("start", start_command))
