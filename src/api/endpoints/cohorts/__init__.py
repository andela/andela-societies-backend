from flask import Blueprint
from flask_restful import Api

from api.endpoints.societies.models import Society
from .models import Cohort
from .crud import Cohorts


cohorts_bp = Blueprint('cohorts', __name__)
cohorts_api = Api(cohorts_bp)


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
