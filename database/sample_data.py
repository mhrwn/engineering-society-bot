# database/sample_data.py
from .models import Event

def get_sample_events():
    """Return sample events data for database initialization"""
    return [
        Event(
            name='کارگاه تست ۱',
            description='آموزش عملی دستگاه CNC',
            date='۱۴۰۴/۱۰/۱۵',
            time='10:00',  # Ensure correct time
            location='سالن شماره ۲',  # Ensure correct location
            capacity=10,
            type='workshop'
        ),
        Event(
            name='رویداد تست ۱',
            description='بررسی آخرین تکنولوژی‌های صنعتی',
            date='۱۴۰۴/۱۰/۲۰',
            time='09:30',  # Ensure correct time
            location='سالن اجتماعات',  # Ensure correct location
            capacity=12,
            type='event'
        ),
        Event(
            name='رویداد تست ۲',
            description='بازدید از خط تولید یک کارخانه',
            date='۱۴۰۴/۱۰/۲۵',
            time='08:00',  # Ensure correct time
            location='کارخانه صنعتی البرز',  # Ensure correct location
            capacity=10,
            type='event'
        )
    ]

def get_sample_event_names():
    """Return list of sample event names for validation"""
    events = get_sample_events()
    return [event.name for event in events]

def get_sample_event_by_name(name):
    """Get sample event by name"""
    events = get_sample_events()
    for event in events:
        if event.name == name:
            return event
    return None