from flask import Blueprint
from flask_restful import Api


from .all_logged_activities import LoggedActivitiesAPI
from .user_logged_activites import UserLoggedActivitiesAPI
from .single_logged_activity import LoggedActivityAPI
from .approve import LoggedActivityApprovalAPI
from .reject import LoggedActivityRejectionAPI
from .request_info import LoggedActivityInfoAPI
from .secretary_review import SecretaryReviewLoggedActivityAPI


logged_activities_bp = Blueprint('api', __name__)
logged_activities_api = Api(logged_activities_bp)


# add or fetch logged activities endpoint
logged_activities_api.add_resource(
    LoggedActivitiesAPI,
    '/logged-activities', '/logged-activities/',
    endpoint='logged_activities'
)

# single logged activity endpoint
logged_activities_api.add_resource(
    LoggedActivityAPI,
    '/logged-activities/<string:logged_activity_id>',
    '/logged-activities/<string:logged_activity_id>/',
    endpoint='logged_activity'
)

# user logged activities endpoint
logged_activities_api.add_resource(
    UserLoggedActivitiesAPI,
    '/users/<string:user_id>/logged-activities',
    '/users/<string:user_id>/logged-activities/',
    endpoint='user_logged_activities'
)

# society secretary logged activity review endpoint
logged_activities_api.add_resource(
    SecretaryReviewLoggedActivityAPI,
    '/logged-activities/review/<string:logged_activity_id>',
    '/logged-activities/review/<string:logged_activity_id>/',
    endpoint='secretary_logged_activity'
)

# success ops request more info on logged activity endpoint
logged_activities_api.add_resource(
    LoggedActivityInfoAPI,
    '/logged-activities/info/<string:logged_activity_id>',
    '/logged-activities/info/<string:logged_activity_id>/',
    endpoint='info_on_logged_activity'
)

# success ops approve logged activities endpoint
logged_activities_api.add_resource(
    LoggedActivityApprovalAPI,
    "/logged-activities/approve",
    "/logged-activities/approve/",
    endpoint="approve_logged_activities"
)

# success ops reject logged_activity
logged_activities_api.add_resource(
    LoggedActivityRejectionAPI,
    "/logged-activity/reject/<string:logged_activity_id>",
    "/logged-activity/reject/<string:logged_activity_id>/",
    endpoint="reject_logged_activity"
)
