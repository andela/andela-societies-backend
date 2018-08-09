"""Testing Suite for all notifications."""
from flask import current_app

from .base_test import BaseTestCase
from ..api.utils.notifications.email_notices import send_email


class TestMailGunNotification(BaseTestCase):
    """Test Class for Email notifications."""

    def test_send_email_with_valid_email(self):
        """
        Happy test.

        This test ensures that the send email task can send an
        email if the email has a subject, message and valid
        recipients email addresses
        """
        self.assertTrue(send_email(
            sender=current_app.config["SENDER_CREDS"],
            subject="Test email",
            message="This is a test message",
            recipients=["test.fellow@andela.com"]
        ))

    def test_send_email_with_invalid_email(self):
        """
        Sad Test.

        This test ensures that the send email task can not send an
        email if the validation method fails
        """
        self.assertRaises(
            ValueError,
            lambda: send_email(
                sender=current_app.config["SENDER_CREDS"],
                subject="Test email",
                message="This is a test message",
                recipients=["invalid.gmail.com"]
            )
        )

        self.assertRaises(
            ValueError,
            lambda: send_email(
                sender="",
                subject="Test email",
                message="This is a test message",
                recipients=["invalid.gmail.com"]
            )
        )
