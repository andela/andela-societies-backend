from flask_restful import Resource
from flask import request

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder

from .marshmallow_schemas import logged_activities_schema


class LoggedActivityApprovalAPI(Resource):
    """Allows success-ops to approve at least one Logged Activities."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependacy for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']

    @roles_required(["success ops"])
    def put(self, logged_activity_id=None):
        """Put method for approving logged Activity resource."""
        payload = request.get_json(silent=True)

        if payload:
            logged_activities_ids = payload.get('loggedActivitiesIds', None)

            if logged_activities_ids is None:
                return response_builder(dict(
                    message='loggedActivitiesIds is required'), 400)

            if len(logged_activities_ids) > 20:
                return response_builder(dict(
                    message='Sorry, you can not approve more than 20'
                            ' logged_activities at a go'), 403)

            if not isinstance(logged_activities_ids, list) or \
                    not logged_activities_ids:
                return response_builder(dict(
                    message='A List/Array with at least one logged activity'
                            ' id is needed!'), 400)

            unique_activities_ids = set([])
            for logged_activities_id in logged_activities_ids:
                logged_activities = self.LoggedActivity.query.get(
                    logged_activities_id
                )
                if logged_activities is None or logged_activities.redeemed \
                    or logged_activities.status in ['rejected', 'in review',
                                                    'approved']:
                    continue
                unique_activities_ids.add(logged_activities)

            if not unique_activities_ids:
                return response_builder(dict(
                    status='failed',
                    message='Invalid logged activities or no pending logged'
                            ' activities in request'),
                    400)
            else:
                for unique_activities_id in list(unique_activities_ids):
                    unique_activities_id.status = 'approved'
                    unique_activities_id.society.total_points = \
                        unique_activities_id

                user_logged_activities = logged_activities_schema.dump(
                    unique_activities_ids).data

                # NOTE: this code works as expected, shipping it out for the
                # MVP further optimization will be done from line 319 - 325
                # using marshmallow
                for user_logged_activity in user_logged_activities:
                    user_logged_activity['society'] = {
                        'id': user_logged_activity['societyId'],
                        'name': user_logged_activity['society']
                    }
                    del user_logged_activity['society']['id']
                    del user_logged_activity['societyId']
                return response_builder(dict(
                    data=user_logged_activities,
                    message='Activity edited successfully'),
                    200)
        else:
            return response_builder(dict(
                message='Data for creation must be provided.'),
                400)
