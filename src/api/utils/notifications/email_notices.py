"""Notifications module."""
import re
import os
import requests
from flask import current_app
from celery import Celery


celery = Celery(
    "notifications",
    broker=os.environ.get("CELERY_BROKER_URL", None),
    backend=os.environ.get("CELERY_BACKEND", None)
)


def validate_email(recipients=None):
    """
    Eliminating emails sent to invalid emails.

    This method validates that the recipients list has valid
    email addresses before send() is invoked
    :return bool:
    """
    regex = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
    for email in recipients:
        if not re.match(regex, email):
            raise ValueError("invalid email address: {}".format(email))
    return True


@celery.task()
def send_email(**kwargs):
    """
    Send the Emails.

    This method sends email using Mail Gun. Ensure to have the following
    environment variable set;
    1. MAIL_GUN_URL
    2. MAIL_GUN_API_KEY

    :kwarg app:
    :kwarg strategy:
    :kwarg subject:
    :kwarg message:
    :kwarg sender:
    :kwarg recipients:
    :return bool:
    """
    mail_gun_url = current_app.config["MAIL_GUN_URL"]
    mail_gun_api_key = current_app.config["MAIL_GUN_API_KEY"]
    mail_gun_test = current_app.config.get("MAIL_GUN_TEST")

    if kwargs["sender"] == "":
        raise ValueError("sender address missing")

    if mail_gun_test:
        if validate_email(kwargs["recipients"]):
            return True

    if validate_email(kwargs["recipients"]):
        response = requests.post(
            mail_gun_url,
            auth=("api", mail_gun_api_key),
            data={
                "from": kwargs["sender"],
                "to": kwargs["recipients"],
                "subject": kwargs["subject"],
                "text": kwargs["message"]
            }
        )
        if response.status_code == 200:
            return True
        else:
            return False
