"""setup societies request resource blueprint."""


def societies_bp(Api, Blueprint):
    from .models import Society
    from .crud import SocietyResource

    societies_bp_service = Blueprint('societies', __name__)
    societies_api = Api(societies_bp_service)

    # society CRUD endpoints
    societies_api.add_resource(
        SocietyResource,
        "/societies",
        "/societies/",
        "/societies/<string:society_id>",
        "/societies/<string:society_id>/",
        endpoint="societies",
        resource_class_kwargs={
            'Society': Society
        }
    )
    return societies_bp_service
