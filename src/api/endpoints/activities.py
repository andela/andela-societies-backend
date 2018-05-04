"""Activities Module."""
from flask import g, jsonify, request
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.models import Activity
from api.utils.marshmallow_schemas import activity_schema


class ActivitiesAPI(Resource):
    """contains CRUD endpoints for activities."""

    @token_required
    @roles_required(["Success Ops"])
    def post(self):
        """Create an activity."""
        payload = request.get_json()

        result, errors = activity_schema.load(payload)

        if errors:
            response = jsonify(errors)
            status_code = activity_schema.context.get('status_code')
            activity_schema.context = {}
            response.status_code = status_code or 400
        else:
            activity = Activity(name=result['name'],
                                description=result['description'],
                                activity_type_id=result['activity_type_id'],
                                activity_date=result['activity_date'],
                                added_by_id=g.current_user.uuid
                                )
            activity.save()

            response = jsonify({'message': 'Activity created successfully.',
                                'data': result})
            response.status_code = 201

        return response
