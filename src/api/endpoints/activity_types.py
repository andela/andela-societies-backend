"""Module for activity types operations."""

from flask_restplus import Resource

from api.utils.auth import token_required
from api.models import ActivityType
from api.utils.marshmallow_schemas import activity_types_schema
from api.utils.helpers import response_builder


class ActivityTypesAPI(Resource):
    """Activity Categories Resource."""

    @token_required
    def get(self):
        """Get information on activity types."""
        activity_types = ActivityType.query.all()

        activity_types_list = activity_types_schema.dump(
            activity_types).data

        return response_builder(dict(data=activity_types_list), 200)
