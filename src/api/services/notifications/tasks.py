"""Notifications module."""
import os

from flask import current_app
from flask_mail import Mail
from flask_mail import Message
from celery import Celery
from celery.schedules import crontab

from api.services.notifications.helpers import (
    generate_success_ops_pending_activities_emails,
    create_celery_flask, validate_email
)


flask_app = create_celery_flask()
celery = Celery(
    "notifications",
    broker=os.environ.get("CELERY_BROKER_URL", None),
    backend=os.environ.get("CELERY_BACKEND", None)
)
mail_sender = Mail()
mail_sender.init_app(flask_app)


celery.conf.beat_schedule = {
    'mail-success-ops': {
        'task': 'api.services.notifications.tasks.mail_success_ops',
        'schedule': crontab(
            hour=9, minute=0,  # timezone is UTC by default
            day_of_week=flask_app.config['SUCCESS_OPS_NEWSLETTER_DAY']
        )
    }
}


@celery.task
def send_email(app=flask_app, mail=mail_sender, **kwargs):
    """
    Send the Emails.

    This method sends email using Flask_Mail. Ensure to have the following
    environment variable set;
    1. MAIL_SERVER = Your Server
    2. MAIL_PORT = Your server's port
    3. MAIL_USE_TLS = True
    4. MAIL_USERNAME
    5. MAIL_PASSWORD

    :kwarg app:
    :kwarg strategy:
    :kwarg subject:
    :kwarg message:
    :kwarg sender:
    :kwarg recipients:
    :return bool:
    """
    with app.app_context():
        if not kwargs.get("sender") or not kwargs.get("sender").strip():
            raise ValueError("sender address missing")

        validate_email(kwargs["recipients"])

        if current_app.config.get("MAIL_GUN_TEST"):
                return True

        msg = Message(subject=kwargs["subject"],
                      recipients=kwargs["recipients"], sender=kwargs["sender"])
        msg.body = kwargs["message"]

        if kwargs.get("html"):
            msg.html = kwargs.get("html")

        mail_sender.send(msg)


@celery.task
def mail_success_ops(app=flask_app):
    """
    Mail Cron Job.

    Mail success ops every monday morning when there are pending
    activities
    """
    emails_kwargs_tuple = generate_success_ops_pending_activities_emails(app)
    if isinstance(emails_kwargs_tuple, tuple):
        for email_kwargs in emails_kwargs_tuple[1]:
            send_email.delay(**email_kwargs)

    return emails_kwargs_tuple
