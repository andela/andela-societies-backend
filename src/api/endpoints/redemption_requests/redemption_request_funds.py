# system imports
from flask import request, g, current_app
from flask_restful import Resource

# imports from other packages
from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder
from api.utils.marshmallow_schemas import basic_info_schema

# import from this package
from .helpers import serialize_redmp


class RedemptionRequestFunds(Resource):
    """
    Mark Redemption Requests are complete.

    The Finance Department marks the redemption request as complete once the
    funds have been sent out.
    """

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.RedemptionRequest = kwargs['RedemptionRequest']
        self.email = kwargs['email']
        self.mail = kwargs['mail']
        self.Role = kwargs['Role']

    @roles_required(["finance"])
    def put(self, redeem_id=None):
        """Complete Redemption Requests and mark them so."""
        payload = request.get_json(silent=True)

        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

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

        status = payload.get("status")

        if status == "completed":
            redemp_request.status = status

            CIO = self.Role.query.filter_by(name='cio').first()
            if CIO and CIO.users.all():  # TODO Add logging here
                email_payload = dict(
                    sender=current_app.config["SENDER_CREDS"],
                    subject="RedemptionRequest for {}".format(
                        redemp_request.user.society.name),
                    message="Redemption Request on {} has been completed. Finance"
                    " has wired the money to the reciepient.".format(
                        redemp_request.name),
                    recipients=([user.email for user in CIO.users]
                                + [redemp_request.user.email])
                )

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

        redemp_request.save()
        mes = f"Redemption request status changed to {redemp_request.status}."

        serialized_redemption = serialize_redmp(redemp_request)
        serialized_completed_by, _ = basic_info_schema.dump(g.current_user)
        serialized_redemption["completedBy"] = serialized_completed_by

        return response_builder(dict(
            status="success",
            data=serialized_redemption,
            message=mes
        ), 200)
