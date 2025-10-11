from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    full_name = Column(String(100), nullable=False)
    student_id = Column(String(20), nullable=False)
    national_id = Column(String(10), nullable=False)
    phone_number = Column(String(11), nullable=False)
    event_name = Column(String(100), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')
    notified_admin = Column(Boolean, default=False)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    date = Column(String(10))
    time = Column(String(10))  # زمان برگزاری
    location = Column(String(100))  # محل برگزاری
    capacity = Column(Integer)
    type = Column(String(20), default='event')
    registered_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)

class UserMessage(Base):
    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_full_name = Column(String(100))
    message_text = Column(Text, nullable=False)
    message_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='unread')
    admin_reply = Column(Text)
    reply_date = Column(DateTime)
    replied_by = Column(Integer)
    message_type = Column(String(20), default='contact')
