"""Notifications module."""
import os
import requests

from celery import Celery
from celery.schedules import crontab

from api.utils.notifications.task_helpers import (
    generate_success_ops_pending_activities_emails,
    create_celery_flask, validate_email
)


flask_app = create_celery_flask()
celery = Celery(
    "notifications",
    broker=os.environ.get("CELERY_BROKER_URL", None),
    backend=os.environ.get("CELERY_BACKEND", None)
)

celery.conf.beat_schedule = {
    'mail-success-ops': {
        'task': 'api.utils.notifications.email_notices.mail_success_ops',
        'schedule': crontab(
            hour=7, minute=30,
            day_of_week=flask_app.config['SUCCESS_OPS_NEWSLETTER_DAY']
        )
    }
}


@celery.task
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
    if not kwargs["sender"] or not kwargs["sender"].strip():
        raise ValueError("sender address missing")

    validate_email(kwargs["recipients"])

    if os.getenv("MAIL_GUN_TEST"):
            return True

    mail_gun_url = flask_app.config["MAIL_GUN_URL"]
    mail_gun_api_key = flask_app.config["MAIL_GUN_API_KEY"]

    data = {
        "from": kwargs["sender"],
        "to": kwargs["recipients"],
        "subject": kwargs["subject"],
        "text": kwargs["message"],
    }
    if kwargs.get("html"):
        data.update(dict(html=kwargs.get("html")))
    response = requests.post(
        mail_gun_url, auth=("api", mail_gun_api_key), data=data
    )
    if response.status_code == 200:
        return True
    else:
        return False


@celery.task
def mail_success_ops(app=flask_app):
    """
    Mail success ops every monday morning when there are pending
    activities
    """
    emails_kwargs_tuple = generate_success_ops_pending_activities_emails(app)
    if isinstance(emails_kwargs_tuple, tuple):
        for email_kwargs in emails_kwargs_tuple[1]:
            send_email.delay(**email_kwargs)

    return emails_kwargs_tuple
