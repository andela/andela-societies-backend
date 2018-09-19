from threading import Thread
import os
from flask_mail import Message


def construct_email_mes(subject, sender, recipients, body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = body
    return msg


def send_email(app, message, mail):
    with app.app_context():
        mail.send(message)


def send_email_async(app, **kwargs):
    payload = kwargs['payload']
    mail = kwargs['mail']
    message = construct_email_mes(
        payload['subject'],
        payload['sender'],
        payload['recipients'],
        payload['message']
    )

    environment = os.environ.get('APP_SETTINGS')
    allowed_env = ["production", "staging", "development"]
    if environment and (environment.lower() in allowed_env):
        Thread(target=send_email, args=(app, message, mail)).start()
    else:
        return message
