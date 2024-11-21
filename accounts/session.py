import threading
from datetime import date

class SessionData:
    _thread_local = threading.local()

    @staticmethod
    def set_session_info(tenant_name: str, action_date: date, value_date: date, user_id: str, user_name: str):
        SessionData._thread_local.session_info = {
            'tenant_name': tenant_name,
            'action_date': action_date,
            'value_date': value_date,
            'user_id': user_id,
            'user_name': user_name
        }

    @staticmethod
    def get_session_info():
        return getattr(SessionData._thread_local, 'session_info', None)

    @staticmethod
    def update_session_info(**kwargs):
        if hasattr(SessionData._thread_local, 'session_info'):
            SessionData._thread_local.session_info.update(kwargs)

class ReadOnlySession:
    @staticmethod
    def get_session_info():
        return SessionData.get_session_info()