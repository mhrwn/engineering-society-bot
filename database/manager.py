# database/manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from datetime import datetime
from .models import Base, Registration, Event, UserMessage
from .sample_data import get_sample_events
from config import Config
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=None):
        """Initialize database connection and create tables."""
        if not db_path:
            db_path = Config.DATABASE_PATH
        
        # Create database directory if not exists
        Path(db_path).parent.mkdir(exist_ok=True)
        
        # Database engine with connection pooling
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={'timeout': 30}
        )
        
        # Create tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize database with sample events if empty."""
        session = self.Session()
        try:
            if session.query(Event).count() == 0:
                sample_events = get_sample_events()
                session.add_all(sample_events)
                session.commit()
                logger.info("Sample events initialized successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Error initializing sample data: {e}")
        finally:
            session.close()

    def _get_session(self):
        """Return a new database session."""
        return self.Session()

    # Registration Methods
    def add_registration(self, user_id, full_name, student_id, national_id, phone_number, event_name):
        session = self._get_session()
        try:
            event = session.query(Event).filter_by(name=event_name, active=True).first()
            if not event:
                raise ValueError("رویداد یافت نشد")
            if event.registered_count >= event.capacity:
                raise ValueError("ظرفیت رویداد تکمیل است")
            if session.query(Registration).filter_by(user_id=user_id, event_name=event_name).count() > 0:
                raise ValueError("کاربر قبلاً در این رویداد ثبت‌نام کرده است")

            registration = Registration(
                user_id=user_id,
                full_name=full_name,
                student_id=student_id,
                national_id=national_id,
                phone_number=phone_number,
                event_name=event_name
            )
            session.add(registration)
            event.registered_count += 1
            session.commit()
            logger.info(f"Registration added: ID {registration.id}")
            return registration.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in add_registration: {e}")
            raise
        finally:
            session.close()

    def get_events(self, event_type=None):
        session = self._get_session()
        try:
            query = session.query(Event).filter_by(active=True)
            if event_type:
                query = query.filter_by(type=event_type)
            events = query.order_by(Event.date).all()
            return [(e.name, e.description, e.date, e.capacity, e.registered_count, e.type) for e in events]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_events: {e}")
            return []
        finally:
            session.close()

    def is_user_registered_for_event(self, user_id, event_name):
        session = self._get_session()
        try:
            return session.query(Registration).filter_by(user_id=user_id, event_name=event_name).count() > 0
        except SQLAlchemyError as e:
            logger.error(f"Database error in is_user_registered_for_event: {e}")
            return False
        finally:
            session.close()

    # Event Management Methods
    def add_event(self, name, description, date, capacity, event_type='event'):
        session = self._get_session()
        try:
            if session.query(Event).filter_by(name=name).first():
                raise ValueError("رویداد با این نام قبلاً وجود دارد")

            event = Event(name=name, description=description, date=date, capacity=capacity, type=event_type)
            session.add(event)
            session.commit()
            logger.info(f"Event added: {name}")
            return event.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in add_event: {e}")
            raise
        finally:
            session.close()

    def toggle_event(self, event_id):
        session = self._get_session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                raise ValueError("رویداد با این شناسه یافت نشد")
            
            event.active = not event.active
            session.commit()
            logger.info(f"Event {event_id} toggled to {'active' if event.active else 'inactive'}")
            return event.active
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in toggle_event: {e}")
            raise
        finally:
            session.close()

    def delete_event(self, event_id):
        session = self._get_session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                raise ValueError("رویداد با این شناسه یافت نشد")
            
            if session.query(Registration).filter_by(event_name=event.name).count() > 0:
                raise ValueError("امکان حذف رویداد با ثبت‌نام‌های فعال وجود ندارد")
            
            session.delete(event)
            session.commit()
            logger.info(f"Event {event_id} deleted")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in delete_event: {e}")
            raise
        finally:
            session.close()

    def update_event(self, event_id, **kwargs):
        session = self._get_session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                raise ValueError("رویداد با این شناسه یافت نشد")
            
            # Handle name uniqueness check
            if 'name' in kwargs and kwargs['name'] != event.name:
                if session.query(Event).filter_by(name=kwargs['name']).first():
                    raise ValueError("رویداد با این نام قبلاً وجود دارد")
                event.name = kwargs['name']
            
            # Handle capacity validation
            if 'capacity' in kwargs:
                if kwargs['capacity'] < event.registered_count:
                    raise ValueError("ظرفیت جدید نمی‌تواند کمتر از تعداد ثبت‌نام‌ها باشد")
                event.capacity = kwargs['capacity']
            
            # Update other fields
            updatable_fields = ['description', 'date', 'type']
            for field in updatable_fields:
                if field in kwargs:
                    setattr(event, field, kwargs[field])
            
            session.commit()
            logger.info(f"Event {event_id} updated")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in update_event: {e}")
            raise
        finally:
            session.close()

    # Message Management Methods
    def add_user_message(self, user_id, user_full_name, message_text, message_type='contact'):
        session = self._get_session()
        try:
            message = UserMessage(
                user_id=user_id,
                user_full_name=user_full_name,
                message_text=message_text,
                message_type=message_type
            )
            session.add(message)
            session.commit()
            logger.info(f"User message added: ID {message.id}")
            return message.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in add_user_message: {e}")
            raise
        finally:
            session.close()

    def get_user_messages_today(self, user_id):
        session = self._get_session()
        try:
            today = datetime.now().date()
            return session.query(UserMessage).filter(
                UserMessage.user_id == user_id,
                UserMessage.message_date >= today
            ).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_messages_today: {e}")
            return 0
        finally:
            session.close()

    def get_all_messages(self, status=None, limit=None):
        session = self._get_session()
        try:
            query = session.query(UserMessage)
            if status:
                query = query.filter_by(status=status)
            if limit:
                query = query.limit(limit)
            messages = query.order_by(UserMessage.message_date.desc()).all()
            return [self._message_to_tuple(m) for m in messages]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_messages: {e}")
            return []
        finally:
            session.close()

    def get_message_by_id(self, message_id):
        session = self._get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            return self._message_to_tuple(message) if message else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_message_by_id: {e}")
            return None
        finally:
            session.close()

    def mark_message_as_read(self, message_id, admin_id):
        session = self._get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                message.status = 'read'
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in mark_message_as_read: {e}")
            return False
        finally:
            session.close()

    def add_admin_reply(self, message_id, admin_id, reply_text):
        session = self._get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                message.admin_reply = reply_text
                message.replied_by = admin_id
                message.reply_date = datetime.utcnow()
                message.status = 'replied'
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in add_admin_reply: {e}")
            return False
        finally:
            session.close()

    def delete_message(self, message_id):
        session = self._get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                session.delete(message)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in delete_message: {e}")
            return False
        finally:
            session.close()

    # Navigation Methods
    def get_next_message_id(self, current_message_id, status=None):
        session = self._get_session()
        try:
            query = session.query(UserMessage.id)
            if status:
                query = query.filter_by(status=status)
            next_message = query.filter(UserMessage.id > current_message_id).first()
            return next_message[0] if next_message else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_next_message_id: {e}")
            return None
        finally:
            session.close()

    def get_previous_message_id(self, current_message_id, status=None):
        session = self._get_session()
        try:
            query = session.query(UserMessage.id)
            if status:
                query = query.filter_by(status=status)
            prev_message = query.filter(UserMessage.id < current_message_id).first()
            return prev_message[0] if prev_message else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_previous_message_id: {e}")
            return None
        finally:
            session.close()

    # Admin Methods
    def get_recent_registrations(self, limit=10):
        session = self._get_session()
        try:
            registrations = session.query(Registration).order_by(
                Registration.registration_date.desc()
            ).limit(limit).all()
            return [self._registration_to_tuple(r) for r in registrations]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_recent_registrations: {e}")
            return []
        finally:
            session.close()

    def get_all_events_admin(self):
        session = self._get_session()
        try:
            events = session.query(Event).order_by(Event.date).all()
            return [self._event_to_tuple(e) for e in events]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_events_admin: {e}")
            return []
        finally:
            session.close()

    def get_unread_messages_count(self):
        session = self._get_session()
        try:
            return session.query(UserMessage).filter_by(status='unread').count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_unread_messages_count: {e}")
            return 0
        finally:
            session.close()

    # Helper Methods
    def _message_to_tuple(self, message):
        return (message.id, message.user_id, message.user_full_name, message.message_text,
                message.message_date, message.status, message.admin_reply, message.reply_date,
                message.replied_by, message.message_type)

    def _registration_to_tuple(self, registration):
        return (registration.id, registration.user_id, registration.full_name, 
                registration.student_id, registration.national_id, registration.phone_number,
                registration.event_name, registration.registration_date, registration.status,
                registration.notified_admin, 'event')

    def _event_to_tuple(self, event):
        return (event.id, event.name, event.description, event.date, event.capacity,
                event.registered_count, event.type, event.active)
    # User Profile Methods
    def get_user_registrations(self, user_id):
        """Get all registrations for a specific user."""
        session = self._get_session()
        try:
            registrations = session.query(Registration).filter_by(user_id=user_id).order_by(
                Registration.registration_date.desc()
            ).all()
            return [self._registration_to_tuple(reg) for reg in registrations]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_registrations: {e}")
            return []
        finally:
            session.close()

    def get_user_registration_count(self, user_id):
        """Get the number of registrations for a user."""
        session = self._get_session()
        try:
            return session.query(Registration).filter_by(user_id=user_id).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_registration_count: {e}")
            return 0
        finally:
            session.close()

    # Cancel Registration Methods
    def delete_registration(self, registration_id, user_id):
        """Delete a registration by ID and user ID."""
        session = self._get_session()
        try:
            registration = session.query(Registration).filter_by(id=registration_id, user_id=user_id).first()
            if not registration:
                raise ValueError("ثبت‌نام یافت نشد یا شما مجوز حذف آن را ندارید.")
            
            event = session.query(Event).filter_by(name=registration.event_name).first()
            if event:
                event.registered_count -= 1  # کاهش تعداد ثبت‌نام‌ها در رویداد
            
            session.delete(registration)
            session.commit()
            logger.info(f"Registration deleted: ID {registration_id} by user {user_id}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in delete_registration: {e}")
            raise
        finally:
            session.close()

    def get_registration_by_id(self, registration_id, user_id):
        """Get a specific registration by ID and user ID."""
        session = self._get_session()
        try:
            registration = session.query(Registration).filter_by(id=registration_id, user_id=user_id).first()
            return self._registration_to_tuple(registration) if registration else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_registration_by_id: {e}")
            return None
        finally:
            session.close()
