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
    MAIL_GUN_URL = os.environ.get('MAIL_GUN_URL')
    MAIL_GUN_API_KEY = os.environ.get('MAIL_GUN_API_KEY')
    SENDER_CREDS = os.environ.get("SENDER_CREDS")
    NOTIFICATIONS_SENDER = os.getenv('NOTIFICATIONS_SENDER')
    CELERY_BACKEND = os.environ.get("CELERY_BACKEND")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CIO = os.environ.get("CIO")

    SUCCESS_OPS_NEWSLETTER_DAY = os.getenv(
        'SUCCESS_OPS_NEWSLETTER_DAY', 'mon'
        # can be int or valid cron day string
    )


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
    MAIL_GUN_TEST = os.environ.get('MAIL_GUN_TEST')
    NOTIFICATIONS_SENDER = os.getenv('TESTS_NOTIFICATIONS_SENDER',
                                     'notifications@tests.com')


class Staging(Development):
    """Model Staging enviroment config object."""

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


configuration = {
    "Testing": Testing,
    "Development": Development,
    "Production": Config,
    "Staging": Staging
}
