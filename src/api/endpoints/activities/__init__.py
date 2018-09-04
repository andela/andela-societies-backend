"""setup activities request resource blueprint."""


def activities_bp(Api, Blueprint):
    from .models import Activity
    from .activities import ActivitiesAPI

    activities_bp_service = Blueprint('activities_api', __name__)
    activities_api = Api(activities_bp_service)

    # activities endpoints
    activities_api .add_resource(
        ActivitiesAPI,
        '/api/v1/activities',
        '/api/v1/activities/',
        endpoint='activities',
        resource_class_kwargs={
            'Activity': Activity
        }
    )
    return activities_bp_service
