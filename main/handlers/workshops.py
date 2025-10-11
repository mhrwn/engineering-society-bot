from telegram import Update
from main.utils.markdown import escape_markdown
from database import db
import logging

logger = logging.getLogger(__name__)

async def workshops_command(update: Update, context):
    """Handle workshops command."""
    events = db.get_events('workshop')

    if not events:
        await update.message.reply_text(
            "📭 *در حال حاضر هیچ کارگاهی برنامه‌ریزی نشده است\\.*",
            parse_mode='MarkdownV2'
        )
        return

    message = "🎓 *کارگاه‌های آموزشی:*\n\n"
    for event in events:
        if len(event) < 7:
            logger.error(f"Workshop data is incomplete: {event}")
            continue

        name_escaped = escape_markdown(event[0])
        description_escaped = escape_markdown(event[1])
        date_escaped = escape_markdown(event[2])
        time_escaped = escape_markdown(event[5])
        location_escaped = escape_markdown(event[6])
        capacity_escaped = escape_markdown(str(event[3]))
        registered_escaped = escape_markdown(str(event[4]))

        message += (
            f"✨ *{name_escaped}*\n"
            f"📅 *تاریخ برگزاری:* {date_escaped}\n"
            f"⏰ *زمان:* {time_escaped}\n"
            f"📍 *محل:* {location_escaped}\n"
            f"👥 *ظرفیت:* {capacity_escaped}\n"
            f"✅ *ثبت‌نام‌شده:* {registered_escaped}\n"
            f"📝 *توضیحات:* {description_escaped}\n\n"
        )

    await update.message.reply_text(message, parse_mode='MarkdownV2')
