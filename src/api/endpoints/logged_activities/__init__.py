"""setup logged_activities request resource blueprint."""


def logged_activities_bp(Api, Blueprint):
    from api.models import ActivityType, Activity
    from .models import LoggedActivity
    from .crud import LoggedActivitiesAPI
    from .user_logged_activities import UserLoggedActivitiesAPI
    from .approve import LoggedActivityApprovalAPI
    from .reject import LoggedActivityRejectionAPI
    from .request_info import LoggedActivityInfoAPI
    from .secretary_review import SecretaryReviewLoggedActivityAPI

    logged_activities_bp_service = Blueprint('logged_activities_api', __name__)
    logged_activities_api = Api(logged_activities_bp_service)

    # CRUD logged activities endpoint
    logged_activities_api.add_resource(
        LoggedActivitiesAPI,
        '/logged-activities', '/logged-activities/',
        '/logged-activities/<string:logged_activity_id>',
        '/logged-activities/<string:logged_activity_id>/',
        endpoint='logged_activities',
        resource_class_kwargs={
            'Activity': Activity,
            'ActivityType': ActivityType,
            'LoggedActivity': LoggedActivity
        }
    )

    # user logged activities endpoint
    logged_activities_api.add_resource(
        UserLoggedActivitiesAPI,
        '/users/<string:user_id>/logged-activities',
        '/users/<string:user_id>/logged-activities/',
        endpoint='user_logged_activities',
        resource_class_kwargs={
            'LoggedActivity': LoggedActivity
        }
    )

    # society secretary logged activity review endpoint
    logged_activities_api.add_resource(
        SecretaryReviewLoggedActivityAPI,
        '/logged-activities/review/<string:logged_activity_id>',
        '/logged-activities/review/<string:logged_activity_id>/',
        endpoint='secretary_logged_activity',
        resource_class_kwargs={
            'LoggedActivity': LoggedActivity
        }
    )

    # success ops request more info on logged activity endpoint
    logged_activities_api.add_resource(
        LoggedActivityInfoAPI,
        '/logged-activities/info/<string:logged_activity_id>',
        '/logged-activities/info/<string:logged_activity_id>/',
        endpoint='info_on_logged_activity',
        resource_class_kwargs={
            'LoggedActivity': LoggedActivity
        }
    )

    # success ops approve logged activities endpoint
    logged_activities_api.add_resource(
        LoggedActivityApprovalAPI,
        "/logged-activities/approve",
        "/logged-activities/approve/",
        endpoint="approve_logged_activities",
        resource_class_kwargs={
            'LoggedActivity': LoggedActivity
        }
    )

    # success ops reject logged_activity
    logged_activities_api.add_resource(
        LoggedActivityRejectionAPI,
        "/logged-activity/reject/<string:logged_activity_id>",
        "/logged-activity/reject/<string:logged_activity_id>/",
        endpoint="reject_logged_activity",
        resource_class_kwargs={
            'LoggedActivity': LoggedActivity
        }
    )
    return logged_activities_bp_service
