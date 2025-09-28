from telegram import Update
from main.utils.markdown import escape_markdown
from database import db
import logging

logger = logging.getLogger(__name__)

async def events_command(update: Update, context):
    """Handle events command."""
    events = db.get_events('event')

    if not events:
        await update.message.reply_text(
            "📭 *در حال حاضر هیچ رویدادی برنامه‌ریزی نشده است\\.*",
            parse_mode='MarkdownV2'
        )
        return

    message = "📅 *رویدادهای پیش‌رو:*\n\n"
    for event in events:
        name, description, date, capacity, registered, event_type = event
        name_escaped = escape_markdown(name)
        description_escaped = escape_markdown(description)
        date_escaped = escape_markdown(date)

        message += (
            f"✨ *{name_escaped}*\n"
            f"📅 تاریخ: {date_escaped}\n"
            f"👥 ظرفیت: {registered}/{capacity}\n"
            f"📝 {description_escaped}\n\n"
        )

    await update.message.reply_text(message, parse_mode='MarkdownV2')
