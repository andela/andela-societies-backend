from flask import Blueprint
from flask_restful import Api

from .crud import Cohorts


cohorts_bp = Blueprint('cohorts', __name__)
cohorts_api = Api(cohorts_bp)


# CRUD cohorts endpoints
cohorts_api.add_resource(
    Cohorts, "/cohorts", "/cohorts/",
    endpoint='cohorts'
)
