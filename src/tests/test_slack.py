from .base_test import BaseTestCase

class SlackNotifyTestCase(BaseTestCase):
    """Test notifications."""


    def setUp(self):
        """Initialize extended attributes"""
        BaseTestCase.setUp(self)

    def test_connection(self):
        connection = self.sc.rtm_connect()
        if connection:
            self.assertEqual(connection, True)

    def test_bot_exists(self):
        bot_id = "UFKKS8ZJP"
        results = self.sc.api_call("users.list")
        users = results.get("members")
        if users:
            for user in users:
                if user['name'] == "societies_notify":
                    user_id = user["id"]
                    self.assertEqual(bot_id, user_id)
