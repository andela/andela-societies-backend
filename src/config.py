"""Conatain App configurations."""

import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config(object):
    """Model base config object that can inherited by other configs."""

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    BASE_DIR = os.path.dirname(__file__)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    PAGE_LIMIT = 10
    DEFAULT_PAGE = 1
    PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
    API_ISSUER = "accounts.andela.com"
    API_AUDIENCE = "andela.com"
    SENDER_CREDS = os.environ.get("SENDER_CREDS")
    NOTIFICATIONS_SENDER = os.getenv('NOTIFICATIONS_SENDER', SENDER_CREDS)
    CIO = os.environ.get("CIO")
    EMAIL_HOST_SERVICE = os.environ.get("EMAIL_HOST_SERVICE")

    SUCCESS_OPS_NEWSLETTER_DAY = os.getenv(
        'SUCCESS_OPS_NEWSLETTER_DAY', 'mon'
        # can be int or valid cron day string
    )

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class Development(Config):
    """Model Development enviroment config object."""

    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Testing(Config):
    """Model Testing enviroment config object."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE') or \
        "sqlite:///" + Config.BASE_DIR + "/dev_db.sqlite"
    PUBLIC_KEY = os.environ.get('PUBLIC_KEY_TEST')
    ISSUER = "tests"
    API_IDENTIFIER = "tests"
    NOTIFICATIONS_SENDER = os.getenv(
        'TESTS_NOTIFICATIONS_SENDER',
        'Andela Societies Notifications<societies-notifications-tests'
        '@andela.com>'
    )


class Staging(Development):
    """Model Staging enviroment config object."""

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


configuration = {
    "testing": Testing,
    "development": Development,
    "production": Config,
    "staging": Staging
}
