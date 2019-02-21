# system imports
from flask import request, g, current_app
from flask_restful import Resource

# imports from other packages
from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder
from api.utils.marshmallow_schemas import basic_info_schema
from api.services.slack_notify import SlackNotification


# import from this package
from .helpers import serialize_redmp
from .marshmallow_schemas import edit_redemption_request_schema
from api.models import Role, User


class RedemptionRequestNumeration(Resource, SlackNotification):
    """
    Approve or reject Redemption Requests.

    After approval or rejection the relevant society get the result of the
    request reflects on the amount of points.
    Only done by success ops.
    """

    def __init__(self, **kwargs):
        """Inject dependencies for resource."""
        self.RedemptionRequest = kwargs['RedemptionRequest']
        self.Society = kwargs['Society']
        self.email = kwargs['email']
        self.mail = kwargs['mail']
        SlackNotification.__init__(self)

    @token_required
    @roles_required(["success ops", "cio"])
    def put(self, redeem_id=None):
        """Approve or Reject Redemption requests."""
        payload = request.get_json(silent=True)

        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

        result, errors = edit_redemption_request_schema.load(payload)
        if errors:
            return response_builder(errors, 400)

        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        redemp_request = self.RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                data=None,
                status="fail",
                message="Resource does not exist."
            ), 404)

        status = result.get("status")
        comment = result.get("comment")
        rejection_reason = result.get("rejection") or \
            result.get('rejection_reason')

        if status == "approved":
            user = redemp_request.user
            society = self.Society.query.get(user.society_id)
            society.used_points = redemp_request
            redemp_request.status = status

            # Get the relevant Finance Center to respond on RedemptionRequest
            center_emails = {"kampala": ".finance@andela.com"}
            finance_email = redemp_request.center.name.lower() + \
                center_emails.get(
                redemp_request.center.name.lower(),
                "-finance@andela.com"
                )

            email_payload = dict(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="Redemption Request on {} has been approved. Click "
                "the link below <a href='{}'>here</a> to view more "
                "details.".format(
                    redemp_request.name,
                    request.host_url + 'api/v1/societies/redeem/' +
                    redeem_id
                ),
                recipients=[finance_email]
            )

            self.email.send(
                current_app._get_current_object(),
                payload=email_payload,
                mail=self.mail
            )

            email_payload = dict(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="Redemption Request on {} has been approved. Finance"
                " will be in touch.".format(redemp_request.name),
                recipients=[redemp_request.user.email]
            )

            self.email.send(
                current_app._get_current_object(),
                payload=email_payload,
                mail=self.mail
            )
        elif status == "rejected":
            redemp_request.status = status
            redemp_request.rejection = rejection_reason
            email_payload = dict(
                sender=current_app.config["SENDER_CREDS"],
                subject=f"Redemption Request for"
                        f" {redemp_request.user.society.name}",
                message=f"This redemption request has been rejected for this"
                        f" reason: {rejection_reason}",
                recipients=[redemp_request.user.email]
            )

            # Send Slack notification to Society President
            message = f"Redemption Request for" + \
                      f" {redemp_request.user.society.name}" + \
                      f" has been rejected for this" + \
                      f" reason: *{rejection_reason}*"
            user_email = redemp_request.user.email
            slack_id = SlackNotification.get_slack_id(self, user_email)
            SlackNotification.send_message(self, message, slack_id)

            self.email.send(
                current_app._get_current_object(),
                payload=email_payload,
                mail=self.mail
            )
        elif comment:
            email_payload = dict(
                sender=current_app.config["SENDER_CREDS"],
                subject="More Info on RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message=comment,
                recipients=[redemp_request.user.email]
            )  # cover for requesting more information

            self.email.send(
                current_app._get_current_object(),
                payload=email_payload,
                mail=self.mail
            )

        else:
            return response_builder(dict(
                status="Failed",
                message="Invalid status.",
            ), 400)

        redemp_request.comment = comment or redemp_request.comment
        redemp_request.save()
        mes = f"Redemption request status changed to {status}."

        serialized_redemption = serialize_redmp(redemp_request)
        serialized_approved_by, _ = basic_info_schema.dump(g.current_user)
        serialized_redemption["approvedBy"] = serialized_approved_by

        return response_builder(dict(
            status="success",
            data=serialized_redemption,
            message=mes
        ), 200)
