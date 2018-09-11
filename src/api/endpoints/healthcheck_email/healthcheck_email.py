"""Module to test Notifications being sent out."""
# system imports
from flask import request, current_app
from flask_restful import Resource

# Other Package Imports
from api.services.auth import token_required
from api.utils.helpers import response_builder
from api.services.notifications.tasks import send_email

# Imports from this package
from .marshmallow_schema import email_schema


class NotificationsAPI(Resource):
    """
    Notifications Resource.

    Use to confirm that Notifications are actually being sent out.
    """

    decorators = [token_required]

    @classmethod
    def post(cls):
        """Trigger send of email to predetermined email address."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                                    message="Data for sending must "
                                            "be provided.",
                                    status="fail",
                                    ), 400)

        result, _ = email_schema.load(payload)

        recipient = result.get("recipient")

        if not recipient:
            return response_builder(dict(
                                    message="recipient of email mandatory",
                                    status="fail",
                                    ), 400)

        send_email.delay(
            sender=current_app.config["SENDER_CREDS"],
            subject="Test Email Notifications",
            message="This is a test email to confirm the notifications work",
            recipients=[recipient]
        )

        return response_builder(dict(
                    status="success",
                    message="Email sent to {} successfully.".format(recipient)
        ), 200)
