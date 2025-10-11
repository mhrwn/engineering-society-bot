# database/__init__.py
from .manager import DatabaseManager
from .models import Base, Registration, Event, UserMessage
from .sample_data import get_sample_events

# Global database instance
db = DatabaseManager()

# Export public interfaces
__all__ = [
    'db',
    'Base', 
    'Registration', 
    'Event', 
    'UserMessage',
    'get_sample_events',
    'DatabaseManager'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Engineering Society Bot'