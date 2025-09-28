from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_main_menu():
    """منوی اصلی ادمین"""
    keyboard = [
        [InlineKeyboardButton("📊 گزارش‌ها و آمار", callback_data="admin_reports")],
        [InlineKeyboardButton("📅 مدیریت رویدادها", callback_data="admin_events")],
        [InlineKeyboardButton("🎓 مدیریت کارگاه‌ها", callback_data="admin_workshops")],
        [InlineKeyboardButton("💬 مدیریت پیام‌ها", callback_data="admin_messages")],
        [InlineKeyboardButton("📢 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 خروج از حالت ادمین", callback_data="admin_exit")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_keyboard():
    """دکمه بازگشت به منوی اصلی"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="admin_main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_report_types_keyboard():
    """صفحه‌کلید انواع گزارش‌ها"""
    keyboard = [
        [InlineKeyboardButton("📋 گزارش ثبت‌نام‌ها", callback_data="report_registrations")],
        [InlineKeyboardButton("👥 گزارش کاربران", callback_data="report_users")],
        [InlineKeyboardButton("📈 آمار کلی", callback_data="report_stats")],
        [InlineKeyboardButton("📄 گزارش PDF رویدادها", callback_data="report_pdf")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_date_range_keyboard():
    """صفحه‌کلید بازه‌های زمانی"""
    keyboard = [
        [InlineKeyboardButton("📅 امروز", callback_data="date_range_today")],
        [InlineKeyboardButton("📅 این هفته", callback_data="date_range_this_week")],
        [InlineKeyboardButton("📅 این ماه", callback_data="date_range_this_month")],
        [InlineKeyboardButton("📅 همه زمان‌ها", callback_data="date_range_all_time")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_cancel_keyboard():
    """صفحه‌کلید تأیید/لغو"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data="confirm_action"),
            InlineKeyboardButton("❌ لغو", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_event_management_keyboard():
    """صفحه‌کلید مدیریت رویدادها"""
    keyboard = [
        [InlineKeyboardButton("➕ افزودن رویداد جدید", callback_data="event_add")],
        [InlineKeyboardButton("✏️ ویرایش رویداد", callback_data="event_edit")],
        [InlineKeyboardButton("👀 مشاهده رویدادها", callback_data="event_view")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
