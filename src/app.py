"""Main app module."""

from blinker import Namespace
from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from flask_mail import Mail
from flask_restful import Api

from api.endpoints.logged_activities import logged_activities_bp
from api.endpoints.cohorts import cohorts_bp
from api.endpoints.societies import societies_bp
from api.endpoints.activities import activities_bp
from api.endpoints.redemption_requests import redemption_bp
from api.endpoints.roles import roles_bp
from api.endpoints.activity_types import activitiy_type_bp
from api.endpoints.users import users_bp
from api.models import Base


try:
    from .config import configuration
    from .email_handeler import send_email_async
except ImportError:
    from config import configuration
    from email_handeler import send_email_async


db = Base.db


def create_app(environment="Production"):
    """Create an instance of the app with the given env.

    Args:
        environment (str): Specify the configuration to initialize app with.

    Return:
        app (Flask): it returns an instance of Flask.
    """
    app = Flask(__name__)
    app.config.from_object(configuration[environment])
    db.init_app(app)

    mail = Mail(app)
    mail.init_app(app)

    # enable cross origin resource sharing
    CORS(app)

    # url prefixes
    url_version_1 = '/api/v1'

    # create events
    app_signals = Namespace()
    send_email_signal = app_signals.signal('send_email')
    send_email_signal.connect(send_email_async)

    # register logged activities blueprint
    app.register_blueprint(
        logged_activities_bp(Api, Blueprint, send_email_signal, mail),
        url_prefix=url_version_1
    )

    # register cohorts blueprint
    app.register_blueprint(
        cohorts_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # register societies blueprint
    app.register_blueprint(
        societies_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # register redemption blueprint
    app.register_blueprint(
        redemption_bp(Api, Blueprint, send_email_signal, mail),
        url_prefix=url_version_1
    )

    # register activities blueprint
    app.register_blueprint(
        activities_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # register roles blueprint
    app.register_blueprint(
        roles_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # register activity_types blueprint
    app.register_blueprint(
        activitiy_type_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # register users blueprint
    app.register_blueprint(
        users_bp(Api, Blueprint),
        url_prefix=url_version_1
    )

    # enable health check ping to API
    @app.route('/')
    def health_check_url():
        response = jsonify(dict(message='Welcome to Andela societies API.'))
        response.status_code = 200
        return response

    # handle default 404 exceptions with a custom response
    @app.errorhandler(404)
    def resource_not_found(error):
        response = jsonify(dict(
            error='Not found',
            message='The requested URL was not found on the server.'))
        response.status_code = 404
        return response

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(
            error='Internal server error',
            message="The server encountered an internal error."))
        response.status_code = 500
        return response

    return app
