"""
celery module
"""
import re
import os
import requests
from celery import Celery


celery = Celery(
    "notifications",
    broker=os.environ.get("CELERY_BROKER_URL", None),
    backend=os.environ.get("CELERY_BACKEND", None)
)


def validate_email(recipients=None):
    """
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
    try:
        mail_gun_url = os.environ.get("MAIL_GUN_URL", None)
        mail_gun_api_key = os.environ.get("MAIL_GUN_API_KEY", None)
        mail_gun_test = os.environ.get("MAIL_GUN_TEST", False)

        if kwargs["sender"] == "":
            raise ValueError("sender address missing")

        if mail_gun_test:
            # todo: create a mock object for mail gun to use here
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
            return True if response is not None and response.status_code == 200 else False
    except KeyError:
        return False
