"""setup user resource blueprint."""


def users_bp(Api, Blueprint):
    from api.models import Center, Cohort
    from .models import User
    from .users import UserAPI

    users_bp_service = Blueprint('users_api', __name__)
    users_api = Api(users_bp_service)

    # user endpoints
    users_api.add_resource(
        UserAPI,
        '/users/<string:user_id>',
        '/users/<string:user_id>/',
        endpoint='user_info',
        resource_class_kwargs={
            'User': User,
            'Center': Center,
            'Cohort': Cohort
        }
    )
    return users_bp_service
