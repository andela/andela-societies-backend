"""setup activitiy_type request resource blueprint."""


def activitiy_type_bp(Api, Blueprint):
    from .models import ActivityType
    from .activity_types import ActivityTypesAPI

    activitiy_type_bp_service = Blueprint('activitiy_type_api', __name__)
    activitiy_type_api = Api(activitiy_type_bp_service)

    # activity types endpoints
    activitiy_type_api.add_resource(
        ActivityTypesAPI,
        '/activity-types',
        '/activity-types/',
        '/activity-types/<string:act_types_id>',
        '/activity-types/<string:act_types_id>/',
        endpoint='activity_types',
        resource_class_kwargs={
            'ActivityType': ActivityType
        }
    )
    return activitiy_type_bp_service
