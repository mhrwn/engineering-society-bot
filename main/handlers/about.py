from telegram import Update
from main.utils.markdown import escape_markdown
from config import Config
import logging

logger = logging.getLogger(__name__)

async def about_command(update: Update, context):
    """Handle about command."""
    society_name_escaped = escape_markdown(Config.SOCIETY_NAME)
    university_escaped = escape_markdown(Config.UNIVERSITY)
    channel_username_escaped = escape_markdown(Config.CHANNEL_USERNAME)

    message_text = (
        f"📖 *درباره {society_name_escaped}*\n\n"
        f"انجمن علمی مهندسی ساخت و تولید با هدف ارتقای سطح علمی و مهارتی دانشجویان فعالیت می‌کند\\.\n\n"
        f"🎯 *اهداف:*\n"
        f"• برگزاری کارگاه‌های آموزشی\n"
        f"• سازماندهی سمینارها و همایش‌ها\n"
        f"• ارتباط با صنعت\n"
        f"• پشتیبانی از پروژه‌های دانشجویی\n\n"
        f"🏛 {university_escaped}\n\n"
        f"📢 *کانال ما:* {channel_username_escaped}"
    )

    await update.message.reply_text(
        message_text,
        parse_mode='MarkdownV2'
    )