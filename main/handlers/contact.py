from telegram import Update
from main.utils.markdown import escape_markdown
from config import Config
import logging

logger = logging.getLogger(__name__)

def create_contact_message():
    """Create the contact message with escaped values."""
    society_name_escaped = escape_markdown(Config.SOCIETY_NAME)
    university_escaped = escape_markdown(Config.UNIVERSITY)
    contact_phone_escaped = escape_markdown(Config.CONTACT_PHONE)
    contact_email_escaped = escape_markdown(Config.CONTACT_EMAIL)
    channel_username_escaped = escape_markdown(Config.CHANNEL_USERNAME)

    return (
        f"📞 *راه‌های ارتباطی با {society_name_escaped}:*\n\n"
        f"📍 آدرس: دانشکده مهندسی مکانیک، {university_escaped}\n"
        f"📞 تلفن: {contact_phone_escaped}\n"
        f"📧 ایمیل: {contact_email_escaped}\n"
        f"📢 کانال: {channel_username_escaped}\n"
        f"🕘 ساعات کاری: ۸\\-۱۶ به جز پنجشنبه‌ها"  # Only escape the hyphen
    )

async def contact_command(update: Update, context):
    """Handle contact command."""
    message_text = create_contact_message()
    await update.message.reply_text(
        message_text,
        parse_mode='MarkdownV2'
    )