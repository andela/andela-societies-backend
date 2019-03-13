from flask_restful import Resource

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder
from api.models import Role, User
from api.services.slack_notify import SlackNotification

from .marshmallow_schemas import single_logged_activity_schema


class LoggedActivityRejectionAPI(Resource, SlackNotification):
    """Allows success-ops to reject at least one Logged Activities."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']
        SlackNotification.__init__(self)

    @roles_required(["success ops"])
    def put(self, logged_activity_id=None):
        """Put method for rejecting logged activity resource."""
        if logged_activity_id is None:
            return response_builder(dict(
                message='loggedActivitiesIds is required'), 400)

        logged_activity = self.LoggedActivity.query.filter_by(
            uuid=logged_activity_id).first()

        if not logged_activity:
            return response_builder(dict(message='Logged activity not found'),
                                    404)

        if logged_activity.status == 'pending':
            logged_activity.status = 'rejected'

            user_logged_activity = single_logged_activity_schema.dump(
                logged_activity).data
            user_logged_activity['society'] = {
                'id': user_logged_activity['societyId'],
                'name': user_logged_activity['society']
            }
            del user_logged_activity['societyId']
            
            # Send notification via Slack to the society Secretary
            society_id = logged_activity.society_id
            message = f"REJECTED! Success Ops have rejected {logged_activity.society.name}'s activity "  + \
                      f"points worth {logged_activity.value}, logged on {logged_activity.activity_date}"
            roles = User.query.filter(User.roles.any(Role.name=="society secretary")).all()
            users = User.query.filter_by(society_id=society_id).all()
            SlackNotification.send_notification(self, roles, users, message)

            return response_builder(dict(
                data=user_logged_activity,
                message='Activity successfully rejected'),
                200)
        else:
            return response_builder(dict(
                status='failed',
                message='This logged activity is either in-review,'
                ' approved or already rejected'), 403)
