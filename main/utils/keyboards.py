from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from main.utils.markdown import escape_markdown  # Add import for escape_markdown

def create_main_keyboard():
    """Create the main reply keyboard for the bot."""
    keyboard = [
        ["📖 درباره انجمن", "📅 رویدادها"],
        ["🎓 کارگاه‌ها", "📞 تماس با ما"],
        ["👤 مشاهده پروفایل", "💬 تماس با مدیر"],
        ["📝 ثبت‌نام در کارگاه‌ها و رویدادها"]  # ویرایش متن دکمه
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def create_cancel_keyboard():
    """Create cancel-only keyboard for registration process."""
    keyboard = [["❌ لغو ثبت‌نام"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def create_event_selection_keyboard(events):
    """Create a keyboard for event selection."""
    keyboard = []
    for event in events:
        if len(event) < 7:  # Ensure there are enough elements in the tuple
            continue  # Skip this event if data is incomplete
        name, description, date, capacity, registered, time, location = event  # Correct unpacking
        escaped_name = escape_markdown(name)  # Escape event name
        # Fix: Use raw name for callback data without escaping
        button = InlineKeyboardButton(text=escaped_name, callback_data=f"event_{name}")  # Fix callback_data prefix
        keyboard.append([button])
    
    # Ensure the cancel button is correctly indented
    keyboard.append([InlineKeyboardButton("❌ لغو ثبت‌نام", callback_data="cancel_registration")])  # Fix indentation here
    return InlineKeyboardMarkup(keyboard)

def create_back_to_menu_keyboard():
    """Create back to menu keyboard for profile view."""
    keyboard = [["🔙 بازگشت به منو"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def create_profile_management_keyboard(has_registrations):
    """Create keyboard for profile management with cancellation option."""
    if has_registrations:
        keyboard = [
            ["❌ انصراف از ثبت‌نام"],
            ["🔙 بازگشت به منو"]
        ]
    else:
        keyboard = [["🔙 بازگشت به منو"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def create_registration_cancellation_keyboard(registrations):
    """Create inline keyboard for registration cancellation."""
    keyboard = []
    for reg in registrations:
        # unpack only needed fields, support 12 elements
        reg_id = reg[0]
        event_name = reg[6]
        event_date = reg[11] if len(reg) > 11 else "نامشخص"
        escaped_event_name = escape_markdown(event_name)  # Escape event name
        escaped_event_date = escape_markdown(event_date)  # Escape event date
        button_text = f"❌ انصراف از {escaped_event_name} ({escaped_event_date})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"cancel_reg_{reg_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="back_to_profile")])
    return InlineKeyboardMarkup(keyboard)

def create_confirmation_keyboard(registration_id):
    """Create confirmation keyboard for cancellation."""
    keyboard = [
        [InlineKeyboardButton("✅ تایید انصراف", callback_data=f"confirm_cancel_{registration_id}")],
        [InlineKeyboardButton("❌ انصراف از انصراف", callback_data="cancel_cancellation")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_edit_registration_keyboard():
    """Create keyboard for editing registration info."""
    keyboard = [
        [InlineKeyboardButton("✏️ ویرایش نام", callback_data="edit_name")],
        [InlineKeyboardButton("✏️ ویرایش شماره دانشجویی", callback_data="edit_student_id")],
        [InlineKeyboardButton("✏️ ویرایش شماره ملی", callback_data="edit_national_id")],
        [InlineKeyboardButton("✏️ ویرایش شماره تماس", callback_data="edit_phone")],
        [InlineKeyboardButton("✅ تأیید نهایی", callback_data="confirm_final")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_registration")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_progress_indicator(current_step, total_steps):
    """Create visual progress indicator."""
    progress = "🟢" * current_step + "⚪" * (total_steps - current_step)
    return f"\n📊 پیشرفت: {progress}\n"

def create_standalone_cancel_keyboard():
    """Create keyboard for standalone cancel command."""
    return ReplyKeyboardMarkup(
        [["❌ لغو عملیات جاری"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
