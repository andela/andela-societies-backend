"""Module for Activities in Andela."""
from flask import jsonify
from flask_restplus import Resource

from ..utils.auth import token_required
from ..models import Activity


class ActivitiesAPI(Resource):
    """Activity Resource."""
    pass
