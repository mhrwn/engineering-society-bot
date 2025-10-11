# main/utils/markdown.py
def escape_markdown(text):
    """Escape special Markdown characters for safe rendering."""
    if not text:
        return ""
    escape_chars = r'\_*[]()~`>#+-=|{.}!'  # Fix order to properly handle . and ! separately
    return ''.join(['\\' + char if char in escape_chars else char for char in str(text)])

def convert_gregorian_to_jalali(gregorian_date):
    """Convert Gregorian date to Jalali date string with better error handling."""
    try:
        if not gregorian_date:
            return "نامشخص"
        # اگر از قبل رشته است
        if isinstance(gregorian_date, str):
            if '/' in gregorian_date and len(gregorian_date.split('/')) == 3:
                return gregorian_date  # قبلاً شمسی است
            # تلاش برای پارس کردن تاریخ میلادی
            from datetime import datetime
            try:
                gregorian_date = datetime.strptime(gregorian_date, '%Y-%m-%d %H:%M:%S')
            except Exception:
                try:
                    gregorian_date = datetime.strptime(gregorian_date, '%Y-%m-%d')
                except Exception:
                    return "نامشخص"
        # تبدیل مطمئن
        from jdatetime import date as jdate
        if hasattr(gregorian_date, 'year'):
            jalali_date = jdate.fromgregorian(
                year=gregorian_date.year,
                month=gregorian_date.month, 
                day=gregorian_date.day
            )
            return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        return "نامشخص"
    except Exception as e:
        # logger.error(f"Error in date conversion: {e}")
        return "نامشخص"