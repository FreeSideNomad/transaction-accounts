import unittest
import threading
from datetime import date

from accounts.session import ReadOnlySession, SessionData


class TestSessionData(unittest.TestCase):

    def worker(self):
        session_info = ReadOnlySession.get_session_info()
        self.assertIsNotNone(session_info)
        self.assertEqual(session_info['tenant_name'], "Tenant1")
        self.assertEqual(session_info['user_id'], "user123")

    def test_session_data_in_thread(self):
        SessionData.set_session_info(
            tenant_name="Tenant1",
            action_date=date.today(),
            value_date=date.today(),
            user_id="user123",
            user_name="John Doe"
        )

        thread = threading.Thread(target=self.worker)
        thread.start()
        thread.join()
