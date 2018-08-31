"""Main app module."""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api

from api.endpoints.logged_activities import logged_activities_bp
from api.endpoints.cohorts import cohorts_bp
from api.endpoints.societies import societies_bp
from api.endpoints.activity_types import ActivityTypesAPI
from api.endpoints.activities import ActivitiesAPI
from api.endpoints.redemption_requests import redemption_bp
from api.endpoints.users import UserAPI
from api.endpoints.roles import RoleAPI, SocietyRoleAPI
from api.models import db


try:
    from .config import configuration
except ImportError:
    from config import configuration


def create_app(environment="Production"):
    """Create an instance of the app with the given env.

    Args:
        environment (str): Specify the configuration to initilize app with.

    Return:
        app (Flask): it returns an instance of Flask.
    """
    app = Flask(__name__)
    app.config.from_object(configuration[environment])
    db.init_app(app)

    api = Api(app=app)

    # enable cross origin resource sharing
    CORS(app)

    # activities endpoints
    api.add_resource(
        ActivitiesAPI, '/api/v1/activities', '/api/v1/activities/',
        endpoint='activities'
    )

    # activity types endpoints
    api.add_resource(
        ActivityTypesAPI, '/api/v1/activity-types',
        '/api/v1/activity-types/', endpoint='activity_types'
    )

    api.add_resource(
        ActivityTypesAPI,
        '/api/v1/activity-types/<string:act_types_id>',
        '/api/v1/activity-types/<string:act_types_id>/',
        endpoint='activity_types_detail'
    )

    # register logged activities blueprint
    app.register_blueprint(logged_activities_bp, url_prefix='/api/v1')

    # register cohorts blueprint
    app.register_blueprint(cohorts_bp, url_prefix='/api/v1')

    # register societies blueprint
    app.register_blueprint(societies_bp, url_prefix='/api/v1')

    # user endpoints
    api.add_resource(
        UserAPI,
        '/api/v1/users/<string:user_id>',
        '/api/v1/users/<string:user_id>/',
        endpoint='user_info'
    )

    # role endpoints
    api.add_resource(
        RoleAPI, "/api/v1/roles", "/api/v1/roles/",
        endpoint="role"
    )

    api.add_resource(
        RoleAPI, "/api/v1/roles/<string:role_query>",
        "/api/v1/roles/<string:role_query>/",
        endpoint="role_detail"
    )

    api.add_resource(
        SocietyRoleAPI, "/api/v1/roles/society-execs",
        "/api/v1/roles/society-execs/",
        endpoint="society_execs_roles"
    )

    # register blueprints here
    app.register_blueprint(redemption_bp)

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
