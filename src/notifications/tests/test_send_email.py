"""
Test send email task
"""
from src.notifications.celery import send_email
from unittest import TestCase


class TestMailGunNotification(TestCase):
    def test_send_email_with_valid_email(self):
        """
        This test ensures that the send email task can send an
        email if the email has a subject, message and valid
        recipients email addresses
        """
        send_email(
            sender="Mailgun Sandbox <postmaster@sandbox1ce36b0401fd4c929ee864bc19bf44e7.mailgun.org>",
            subject="Test email",
            message="This is a test message",
            recipients=["andela.project@gmail.com"]
        )

    def test_send_email_with_invalid_email(self):
        """
        This test ensures that the send email task can not send an
        email if the validation method fails
        """
        self.assertRaises(
            ValueError,
            lambda: send_email(
                sender="Mailgun Sandbox <postmaster@sandbox1ce36b0401fd4c929ee864bc19bf44e7.mailgun.org>",
                subject="Test email",
                message="This is a test message",
                recipients=["invalid.gmail.com"]
            )
        )
