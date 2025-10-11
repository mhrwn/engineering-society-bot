import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAIN_BOT_TOKEN = os.getenv('MAIN_BOT_TOKEN')
    ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
    ADMIN_CHAT_IDS = [int(x.strip()) for x in os.getenv('ADMIN_CHAT_IDS', '').split(',') if x.strip()]
    SOCIETY_NAME = os.getenv('SOCIETY_NAME', 'انجمن علمی مهندسی ساخت و تولید')
    UNIVERSITY = os.getenv('UNIVERSITY', 'دانشگاه محقق اردبیلی')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'uma.ac.ir')
    CONTACT_PHONE = os.getenv('CONTACT_PHONE', '+0123456789')
    CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1002287176548'))
    CHANNEL_URL = os.getenv('CHANNEL_URL', 'https://t.me/UMA_manufacturing402')
    CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@UMA_manufacturing402')
    PROXY_URL = os.getenv('PROXY_URL')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/bot_data.db')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_MESSAGES_PER_DAY = int(os.getenv('MAX_MESSAGES_PER_DAY', '1'))
    HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '10000'))

    @classmethod
    def validate(cls):
        """Validate required configuration values."""
        if not cls.MAIN_BOT_TOKEN:
            raise ValueError("MAIN_BOT_TOKEN not found")
        if not cls.ADMIN_CHAT_IDS:
            raise ValueError("ADMIN_CHAT_IDS not found")
        if not cls.DATABASE_PATH:
            raise ValueError("DATABASE_PATH not found")
        if not cls.SOCIETY_NAME:
            raise ValueError("SOCIETY_NAME not found")
        if not cls.UNIVERSITY:
            raise ValueError("UNIVERSITY not found")
        if not cls.CHANNEL_URL:
            raise ValueError("CHANNEL_URL not found")
        if not cls.CHANNEL_ID:
            raise ValueError("CHANNEL_ID not found")
        if not cls.CHANNEL_USERNAME:
            raise ValueError("CHANNEL_USERNAME not found")
        if not cls.CONTACT_PHONE:
            raise ValueError("CONTACT_PHONE not found")
        if not cls.CONTACT_EMAIL:
            raise ValueError("CONTACT_EMAIL not found")

    @classmethod
    def is_proxy_configured(cls):
        """بررسی آیا پروکسی تنظیم شده است"""
        return bool(cls.PROXY_URL and cls.PROXY_URL.strip())

    @classmethod
    def get_proxy_settings(cls):
        """دریافت تنظیمات پروکسی"""
        if cls.is_proxy_configured():
            return {
                'proxy_url': cls.PROXY_URL,
                'urllib3_proxy_kwargs': {
                    'username': None,
                    'password': None,
                }
            }
        return None
