'''Module for activity types operations'''
from flask import jsonify
from flask_restplus import Resource

from api.utils.auth import token_required
from api.models import ActivityType
from api.utils.marshmallow_schemas import get_activity_types_schema

class ActivityTypesAPI(Resource):
    """Activity Categories Resource."""

    @token_required
    def get(self):
        """Get information on activity types."""
        activity_types = ActivityType.query.all()

        activity_types_list = get_activity_types_schema.dump(
            activity_types).data

        return jsonify(dict(data=activity_types_list))
