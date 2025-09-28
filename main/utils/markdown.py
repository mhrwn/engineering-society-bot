# main/utils/markdown.py
def escape_markdown(text):
    """Escape special Markdown characters for safe rendering."""
    if not text:
        return ""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in str(text)])

def convert_gregorian_to_jalali(gregorian_date):
    """Convert Gregorian date to Jalali date string."""
    try:
        if not gregorian_date:
            return "نامشخص"
        
        # اگر تاریخ قبلاً شمسی است، همان را برگردان
        if isinstance(gregorian_date, str) and '/' in gregorian_date:
            return gregorian_date
        
        # تبدیل تاریخ میلادی به شمسی
        from jdatetime import date as jdate
        if hasattr(gregorian_date, 'year'):  # اگر شی datetime است
            jalali_date = jdate.fromgregorian(
                year=gregorian_date.year,
                month=gregorian_date.month,
                day=gregorian_date.day
            )
            return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        else:  # اگر رشته است
            return str(gregorian_date)
    except Exception as e:
        print(f"Error converting date: {e}")
        return str(gregorian_date)