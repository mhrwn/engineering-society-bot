from telegram.ext import ConversationHandler

# حالت‌های مدیریت رویدادها
class EventStates:
    AWAITING_TITLE = 1
    AWAITING_DESCRIPTION = 2
    AWAITING_DATE = 3
    AWAITING_CAPACITY = 4
    AWAITING_CONFIRMATION = 5

# حالت‌های مدیریت کارگاه‌ها
class WorkshopStates:
    AWAITING_TITLE = 1
    AWAITING_DESCRIPTION = 2
    AWAITING_DATE = 3
    AWAITING_DURATION = 4
    AWAITING_CAPACITY = 5
    AWAITING_CONFIRMATION = 6

# حالت‌های ارسال همگانی
class BroadcastStates:
    AWAITING_MESSAGE = 1
    AWAITING_CONFIRMATION = 2

# حالت‌های مدیریت پیام‌ها
class MessageStates:
    AWAITING_REPLY = 1

# حالت‌های گزارش‌گیری
class ReportStates:
    AWAITING_DATE_RANGE = 1
    AWAITING_REPORT_TYPE = 2
    AWAITING_CONFIRMATION = 3

# حالت‌های کلی
class AdminStates:
    MAIN_MENU = ConversationHandler.END
    IN_CONVERSATION = 1
