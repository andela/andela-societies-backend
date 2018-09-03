"""setup roles request resource blueprint."""


def roles_bp(Api, Blueprint):
    from api.models import Society, User
    from .models import Role
    from .roles import RoleAPI
    from .society_roles import SocietyRoleAPI

    roles_bp_service = Blueprint('roles_api', __name__)
    roles_api = Api(roles_bp_service)

    # role endpoints
    roles_api.add_resource(
        RoleAPI,
        "/api/v1/roles",
        "/api/v1/roles/",
        "/api/v1/roles/<string:role_query>",
        "/api/v1/roles/<string:role_query>/",
        endpoint="role",
        resource_class_kwargs={
            'Role': Role
        }
    )

    roles_api.add_resource(
        SocietyRoleAPI,
        "/api/v1/roles/society-execs",
        "/api/v1/roles/society-execs/",
        endpoint="society_execs_roles",
        resource_class_kwargs={
            'Role': Role,
            'User': User,
            'Society': Society
        }
    )
    return roles_bp_service
