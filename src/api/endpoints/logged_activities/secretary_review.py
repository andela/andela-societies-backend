from flask_restful import Resource
from flask import request, g

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder

from .marshmallow_schemas import single_logged_activity_schema


class SecretaryReviewLoggedActivityAPI(Resource):
    """Enable society secretary to verify logged activities."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']

    @roles_required(['society secretary'])
    def put(self, logged_activity_id):
        """Put method on logged Activity resource."""
        payload = request.get_json(silent=True)

        if 'status' not in payload:
            return response_builder(dict(message='status is required.'),
                                    400)

        logged_activity = self.LoggedActivity.query.filter_by(
            uuid=logged_activity_id).first()
        if not logged_activity:
            return response_builder(dict(message='Logged activity not found'),
                                    404)

        if logged_activity.society.uuid != g.current_user.society.uuid:
            society = logged_activity.society.name
            return response_builder(dict(
                message=f"Permission denied, you are not a secretary of {society}"
                ),
                403)

        if not (payload.get('status') in ['pending', 'rejected']):
            return response_builder(dict(message='Invalid status value.'),
                                    400)
        logged_activity.status = payload.get('status')
        logged_activity.save()

        return response_builder(
            dict(data=single_logged_activity_schema.dump(logged_activity).data,
                 message="successfully changed status"),
            200)
