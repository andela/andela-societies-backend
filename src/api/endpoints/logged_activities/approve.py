from flask_restful import Resource
from flask import request

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder

from .marshmallow_schemas import logged_activities_schema


class LoggedActivityApprovalAPI(Resource):
    """Allows success-ops to approve at least one Logged Activities."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']
        self.db = kwargs['db']

    @roles_required(["success ops"])
    def put(self, logged_activity_id=None):
        """Put method for approving logged Activity resource."""
        payload = request.get_json(silent=True)

        if payload:
            logged_activities_ids = payload.get('loggedActivitiesIds', None)

            if not logged_activities_ids:
                return response_builder(dict(
                    message='loggedActivitiesIds is required'), 400)

            if not isinstance(logged_activities_ids, list) or not logged_activities_ids:
                return response_builder(dict(
                    message='A List/Array with at least one logged activity'
                            ' id is needed!'), 400)

            if len(logged_activities_ids) > 20:
                return response_builder(dict(
                    message='Sorry, you can not approve more than 20'
                            ' logged_activities at a go'), 403)

            bulk_approval_query = self.LoggedActivity.query.filter(
                    self.LoggedActivity.uuid.in_(payload['loggedActivitiesIds']),
                    self.LoggedActivity.status.in_(['pending']))

            request_approval_data = bulk_approval_query.all()

            request_approval =bulk_approval_query.update({'status': 'approved'},
            synchronize_session=False)

            if request_approval:
                self.db.session.commit()
                return response_builder(dict(
                    data=logged_activities_schema.dump(request_approval_data).data,
                    message='Activity edited successfully'),
                    200)
            else:
                return response_builder(dict(
                    status= 'fail',
                    message='invalid logged_activities_ids or no pending logged activities'
                    ), 400)
        else:
            return response_builder(dict(
                message='Data for creation must be provided.'),
                400)
