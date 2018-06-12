"""Main app module."""

from api.endpoints.activity_types import ActivityTypesAPI
from api.endpoints.activities import ActivitiesAPI
from api.endpoints.societies import (SocietyResource, AddCohort,
                                     PointRedemption,
                                     PointRedemptionRequestNumeration)
from api.endpoints.users import UserAPI
from api.endpoints.logged_activities import UserLoggedActivitiesAPI
from api.endpoints.logged_activities import LoggedActivitiesAPI
from api.endpoints.logged_activities import LoggedActivityAPI
from api.endpoints.roles import RoleAPI, SocietyRoleAPI
from api.models import db
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restplus import Api
from flask_sslify import SSLify

try:
    from .config import configuration
except ImportError:
    from config import configuration


def create_app(environment="Development"):
    """Factory Method that creates an instance of the app with the given env.

    Args:
        environment (str): Specify the configuration to initilize app with.

    Returns:
        app (Flask): it returns an instance of Flask.
    """
    app = Flask(__name__)
    app.config.from_object(configuration[environment])
    db.init_app(app)

    api = Api(
        app=app,
        default='API',
        default_label="Available Endpoints",
        title='🗣️ Andela Societies API 😱',
        version='1.0',
        description="""Andela Societies API Endpoint Documentation 📚""",
        scheme='https')

    # to redirect all incoming production requests to https
    if environment.lower() == "production" or "staging":
        SSLify(app, subdomains=True, permanent=True)

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

    # user logged activities
    api.add_resource(
        LoggedActivitiesAPI,
        '/api/v1/logged-activities', '/api/v1/logged-activities/',
        endpoint='logged_activities'
    )
    api.add_resource(
        LoggedActivityAPI,
        '/api/v1/logged-activities/<string:logged_activity_id>',
        '/api/v1/logged-activities/<string:logged_activity_id>/',
        endpoint='logged_activity'
    )

    api.add_resource(
        UserLoggedActivitiesAPI,
        '/api/v1/users/<string:user_id>/logged-activities',
        '/api/v1/users/<string:user_id>/logged-activities/',
        endpoint='user_logged_activities'
    )

    # user endpoints
    api.add_resource(
        UserAPI,
        '/api/v1/user/<string:user_id>',
        '/api/v1/user/<string:user_id>/',
        endpoint='user_info'
    )

    # society endpoints
    api.add_resource(
        SocietyResource, "/api/v1/societies", "/api/v1/societies/",
        endpoint="society"
    )

    api.add_resource(
        SocietyResource,
        "/api/v1/societies/<string:society_id>",
        "/api/v1/societies/<string:society_id>/",
        endpoint="society_detail"
    )

    api.add_resource(
        PointRedemption, "/api/v1/societies/redeem",
        "/api/v1/societies/redeem/",
        endpoint="point_redemption"
    )

    api.add_resource(
        PointRedemption, "/api/v1/societies/redeem/<string:redeem_id>",
        "/api/v1/societies/redeem/<string:redeem_id>/",
        endpoint="point_redemption_detail"
    )

    api.add_resource(
        PointRedemptionRequestNumeration,
        "/api/v1/societies/redeem/verify/<string:redeem_id>",
        "/api/v1/societies/redeem/verify/<string:redeem_id>/",
        endpoint="point_redemption_numeration"
    )

    # Add Cohort to society
    api.add_resource(
        AddCohort, "/api/v1/societies/cohorts"
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
