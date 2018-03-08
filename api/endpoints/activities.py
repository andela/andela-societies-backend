"""Module for Activities in Andela."""
from flask import jsonify
from flask_restplus import Resource

from api.utils.auth import token_required
from api.models import Activity


class ActivitiesAPI(Resource):
    """Activity Resource."""
    pass
