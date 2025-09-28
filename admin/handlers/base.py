from abc import ABC
from admin.services.database_service import admin_db_service

class BaseHandler(ABC):
    def __init__(self):
        self.db_service = admin_db_service
