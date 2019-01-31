from api.services.slack_notify import SlackNotification
from .base_test import BaseTestCase, ActivityType

class SlackNotifyTestCase(BaseTestCase, SlackNotification):
    """Test notifications."""
    
    
    def setUp(self):
        """Initialize extended attributes"""
        BaseTestCase.setUp(self)
        SlackNotification.__init__(self)

    def test_connection(self):
        connection = self.sc.rtm_connect()
        self.assertEqual(connection, True)

    def test_bot_exists(self):
        bot_id = "UFKKS8ZJP"
        results = self.sc.api_call("users.list")
        users = results.get("members")

        for user in users:
            if user['name'] == "societies_notify":
                user_id = user['id']
        self.assertEqual(bot_id, user_id)

