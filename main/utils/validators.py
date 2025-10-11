# validators.py
import re

def convert_persian_digits(text):
    """Convert Persian/Arabic digits to English digits."""
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    converted_text = ''
    for char in text:
        if char in persian_to_english:
            converted_text += persian_to_english[char]
        else:
            converted_text += char
    
    return converted_text

def validate_full_name(full_name):
    """
    Validate full name:
    - Only Persian letters and space allowed
    - At least two parts (e.g. 'علی احمدی')
    - Each part at least 3 Persian letters
    """
    full_name = full_name.strip()
    # فقط حروف فارسی و فاصله مجاز است
    if not re.fullmatch(r'[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی\s]+', full_name):
        return False
    parts = [p for p in full_name.split() if p]
    if len(parts) < 2:
        return False
    for part in parts:
        # هر بخش باید حداقل ۳ حرف فارسی باشد
        if len(part) < 3 or not re.fullmatch(r'[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]+', part):
            return False
    return True

def validate_student_id(student_id):
    """Validate student ID (minimum 8 digits)."""
    # Convert Persian digits to English first
    student_id_english = convert_persian_digits(student_id)
    return student_id_english.isdigit() and len(student_id_english) >= 8

def validate_national_id(national_id):
    """Validate national ID (exactly 10 digits)."""
    # Convert Persian digits to English first
    national_id_english = convert_persian_digits(national_id)
    return national_id_english.isdigit() and len(national_id_english) == 10

def validate_phone_number(phone_number):
    """Validate phone number (Iranian mobile format: 09xxxxxxxxx)."""
    # Convert Persian digits to English first
    phone_number_english = convert_persian_digits(phone_number)
    return bool(re.match(r'^09\d{9}$', phone_number_english))

def validate_message_text(message_text):
    """Validate message text (minimum 5 characters)."""
    return len(message_text.strip()) >= 5

def validate_iranian_national_id(national_id):
    """Validate Iranian national ID using checksum."""
    if not national_id.isdigit() or len(national_id) != 10:
        return False
    check = int(national_id[9])
    s = sum(int(national_id[i]) * (10 - i) for i in range(9)) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

def validate_student_id_format(student_id):
    """Validate specific university student ID format."""
    return len(student_id) >= 8 and student_id.isdigit()

def validate_phone_number_carrier(phone_number):
    """Validate phone number and identify carrier."""
    carriers = {
        '091': 'همراه اول',
        '099': 'همراه اول',
        '093': 'ایرانسل',
        '090': 'ایرانسل',
        '092': 'ایرانسل'
    }
    for prefix, carrier in carriers.items():
        if phone_number.startswith(prefix):
            return True, carrier
    return False, "ناشناخته"