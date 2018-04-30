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
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE')
    PUBLIC_KEY = os.environ.get('PUBLIC_KEY_TEST')


class Staging(Development):
    """Model Staging enviroment config object."""

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


configuration = {
    "Testing": Testing,
    "Development": Development,
    "Production": Config,
    "Staging": Staging
}
