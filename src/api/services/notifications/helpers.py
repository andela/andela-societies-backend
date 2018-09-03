import os
import re

from flask import Flask, render_template_string

from config import configuration
from api.models import Base, Role, LoggedActivity


SUCCESS_OPS_MESSAGE = '''
Hi {{name}},\n
There are {{count}} pending logged activities. \n
Have a great week ahead.\n
Regards,
The Andela Societies Team.
'''

db = Base.db


def create_celery_flask(environment=os.getenv('APP_SETTINGS', 'Production')):
    """Factory Method that creates an instance of the app with the given env.

    Args:
        environment (str): Specify the configuration to initialize app with.

    Return:
        app (Flask): it returns an instance of Flask.
    """
    app = Flask(__name__)
    app.config.from_object(configuration[environment])
    app.config.update(  # EMAIL SETTINGS
                      MAIL_SERVER=os.environ.get("MAIL_SERVER"),
                      MAIL_PORT=os.environ.get("MAIL_PORT"),
                      MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS"),
                      MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
                      MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD")
                      )
    db.init_app(app)
    return app


def validate_email(recipients=None):
    """
    Eliminating emails sent to invalid emails.

    This method validates that the recipients list has valid
    email addresses before send() is invoked
    :return bool:
    """
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    for email in recipients:
        if not re.match(regex, email):
            raise ValueError("invalid email address: {}".format(email))
    return True


def generate_success_ops_pending_activities_emails(app):
    '''
    Get pending logged activities and genrate email for each success ops
    member
    '''
    with app.app_context():
        success_ops_role = Role.query.filter_by(
            name='success ops'
        ).one_or_none()

        success_ops_members = success_ops_role.users.all() if success_ops_role \
            else None
        if success_ops_members:
            pending_logged_activities_count = LoggedActivity.query.filter_by(
                status='pending'
            ).count()
            if pending_logged_activities_count:
                emails_list = []
                for member in success_ops_members:
                    emails_list.append(dict(
                        subject=f'There are pending logged activities',
                        recipients=[member.email],
                        message=render_template_string(
                            SUCCESS_OPS_MESSAGE, name=member.name,
                            count=pending_logged_activities_count
                        ),
                        sender=app.config['NOTIFICATIONS_SENDER']
                    ))
                db.session.remove()
                return True, emails_list

        db.session.remove()
        return False
