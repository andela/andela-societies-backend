"""setup cohort request resource blueprint."""


def cohorts_bp(Api, Blueprint):
    from api.models import Society
    from .models import Cohort
    from .crud import Cohorts

    cohorts_bp_service = Blueprint('cohorts_api', __name__)
    cohorts_api = Api(cohorts_bp_service)

    # CRUD cohorts endpoints
    cohorts_api.add_resource(
        Cohorts,
        "/cohorts",
        "/cohorts/",
        endpoint='cohorts',
        resource_class_kwargs={
            'Cohort': Cohort,
            'Society': Society
        }
    )
    return cohorts_bp_service
