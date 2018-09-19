from flask_restful import Resource
from flask import request, current_app

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder


class LoggedActivityInfoAPI(Resource):
    """Allows success-ops to request more info on a Logged Activity."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']
        self.email = kwargs['email']
        self.mail = kwargs['mail']

    @roles_required(["success ops"])
    def put(self, logged_activity_id=None):
        """Put method for requesting more info on a logged activity."""
        payload = request.get_json(silent=True)

        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

        if not logged_activity_id:
            return response_builder(dict(
                status="fail",
                message="LoggedActivity id must be provided."), 400)

        logged_activity = self.LoggedActivity.query.get(logged_activity_id)

        if not logged_activity:
            return response_builder(dict(message='Logged activity not found'),
                                    404)

        comment = payload.get("comment")
        if comment:
            email_payload = dict(
                sender=current_app.config["SENDER_CREDS"],
                recipients=[logged_activity.user.email],
                subject="More Info on Logged Activity for {}".format(
                    logged_activity.user.society.name),
                message="Success Ops needs more information on this"
                        " logged activity: {}.\\n Context: {}."
                        "\\nClick <a href='{}'>here</a>"
                        " to view the logged activity and edit the"
                        " description to give more informaton.".format(
                            logged_activity.name, comment, request.host_url +
                            '/api/v1/logged-activities/' +
                            logged_activity.uuid
                            ),
            )
            self.email.send(
                current_app._get_current_object(),
                payload=email_payload,
                mail=self.mail
            )
        else:
            return response_builder(dict(
                status="fail",
                message="Context for extra informaton must be provided."), 400)

        return response_builder(dict(
            status='success',
            message='Extra information has been successfully requested'), 200)
