"""Test Suite for all Notifications."""
import os

from .base_test import BaseTestCase
from api.utils.notifications.email_notices import send_email


class TestMailGunNotification(BaseTestCase):
    """Test Suite on Emails being sent out with MailGun."""

    def setUp(self):
        """Set up all needed variables."""
        BaseTestCase.setUp(self)
        self.mail_creds = os.environ.get("SENDER_CREDS")

    def test_send_email_with_valid_email(self):
        """
        Test send email successful.

        This test ensures that the send email task can send an email if the
        email has a subject, message and valid recipients email addresses.
        """
        send_email(
            sender=self.mail_creds,
            subject="Test email",
            message="This is a test message",
            recipients=["andela.project@gmail.com"]
        )

    def test_send_email_with_invalid_email(self):
        """
        Test send email fails.

        This test ensures that the send email task can not send an email if the
        validation method fails.
        """
        self.assertRaises(
            ValueError,
            lambda: send_email(
                sender=self.mail_creds,
                subject="Test email",
                message="This is a test message",
                recipients=["invalid.gmail.com"]
            )
        )
