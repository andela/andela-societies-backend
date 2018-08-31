from flask import Blueprint
from flask_restful import Api

from .crud import SocietyResource


societies_bp = Blueprint('societies', __name__)
societies_api = Api(societies_bp)


# society CRUD endpoints
societies_api.add_resource(
    SocietyResource,
    "/societies", "/societies/",
    "/societies/<string:society_id>",
    "/societies/<string:society_id>/",
    endpoint="societies"
)
