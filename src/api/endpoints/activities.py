"""Activities Module."""
from flask import g, request
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.models import Activity
from api.utils.marshmallow_schemas import activity_schema
from api.utils.helpers import response_builder


class ActivitiesAPI(Resource):
    """Contains CRUD endpoints for activities."""

    @token_required
    @roles_required(["Success Ops"])
    def post(self):
        """Create an activity."""
        payload = request.get_json(silent=True)

        if payload:
            result, errors = activity_schema.load(payload)

            if errors:
                status_code = activity_schema.context.get('status_code')
                activity_schema.context = {}
                validation_status_code = status_code or 400
                return response_builder(errors, validation_status_code)
            else:
                activity = Activity(
                            name=result['name'],
                            description=result['description'],
                            activity_type_id=result['activity_type_id'],
                            activity_date=result['activity_date'],
                            added_by_id=g.current_user.uuid
                                    )
                activity.save()

                return response_builder(dict(
                                        message='Activity created'
                                        ' successfully.',
                                        data=result), 201)
        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)
