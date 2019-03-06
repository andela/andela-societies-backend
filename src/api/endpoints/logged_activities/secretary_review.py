from flask_restful import Resource
from flask import request, g

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder
from api.models import Role, User
from api.services.slack_notify import SlackNotification

from .marshmallow_schemas import single_logged_activity_schema


class SecretaryReviewLoggedActivityAPI(Resource, SlackNotification):
    """Enable society secretary to verify logged activities."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']
        SlackNotification.__init__(self)

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

        # Send notification to success-ops
        roles = User.query.filter(User.roles.any(Role.name=="success ops")).all()
        users = User.query.all()
        message = f"The society secretary for {logged_activity.society.name} has approved an activity " + \
                  f"worth {logged_activity.value} points. Go to https://societies.andela.com/u/verify-activities to approve or reject these points" # noqa: E501

        logged_activity.status = payload.get('status')
        if logged_activity.status == "pending":
            # Send approved notification to success-ops
            SlackNotification.send_notification(self, roles, users, message)

            # Send approved notification to the respective fellow
            user_email = logged_activity.user.email

            message = f"APPROVED. Your activity points for {logged_activity.description} logged " + \
                      f"on {logged_activity.activity_date} have been approved by your Society's Secretary."
            slack_id = SlackNotification.get_slack_id(self, user_email)
            SlackNotification.send_message(self, message, slack_id)


       # Send notification to a fellow
        if logged_activity.status == "rejected":
            user_email = logged_activity.user.email

            message = f"Your logged society points worth {logged_activity.value} described as " + \
                      f"{logged_activity.description} have been rejected by your Society's Secretary"
            slack_id = SlackNotification.get_slack_id(self, user_email)
            SlackNotification.send_message(self, message, slack_id)

        logged_activity.save()

        return response_builder(
            dict(data=single_logged_activity_schema.dump(logged_activity).data,
                 message="successfully changed status"),
            200)
