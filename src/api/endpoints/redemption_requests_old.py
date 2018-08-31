"""RedemptionRequest Module."""

from flask import request, g, current_app
from flask_restful import Resource

from api.utils.notifications.email_notices import send_email
from api.utils.auth import token_required, roles_required
from api.utils.helpers import (
    find_item, paginate_items, response_builder, get_redemption_request
)
from api.utils.helpers import serialize_redmp
from api.utils.marshmallow_schemas import (
    redemption_request_schema, edit_redemption_request_schema
)
from api.utils.marshmallow_schemas import basic_info_schema, redemption_schema
from api.endpoints.societies.models import Society
from ..models import RedemptionRequest, Center


class PointRedemptionAPI(Resource):
    """
    Resource handling all point redemption requests.

    Only made by society presidents.
    """

    @classmethod
    @token_required
    @roles_required(["society president"])
    def post(cls):
        """Create Redemption Request."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Redemption request must have data.",
                status="fail"
            ), 400)

        result, errors = redemption_request_schema.load(payload)

        if errors:
            return response_builder(errors, 400)

        if result.get('value') > g.current_user.society.remaining_points:
            return response_builder(dict(
                message="Redemption request value exceeds your society's "
                        "remaining points",
                status="fail"
            ), 403)

        center = Center.query.filter_by(name=result.get('center')).first()

        if center:
            redemp_request = RedemptionRequest(
                name=result.get('name'),
                value=result.get('value'),
                description=result.get('description'),
                user=g.current_user,
                center=center,
                society=g.current_user.society
            )
            redemp_request.save()
            data, _ = redemption_schema.dump(redemp_request)
            data["center"], _ = basic_info_schema.dump(center)

            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    g.current_user.society.name),
                message="Redemption Request reason:{}."
                        "Redemption Request value: {} points".format(
                    redemp_request.name, redemp_request.value),
                recipients=[current_app.config["CIO"]]
            )

            return response_builder(dict(
                message="Redemption request created. Success Ops will be in"
                        " touch soon.",
                status="success",
                data=serialize_redmp(redemp_request)
            ), 201)

        else:
            return response_builder(dict(
                message="Redemption request name, value and center required",
                status="fail"
            ), 400)

    @classmethod
    @token_required
    @roles_required(["society president", "success ops"])
    def put(cls, redeem_id=None):
        """Edit Redemption Requests."""
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
                message="Redemption Request to be edited must be provided"),
                400)

        redemp_request = get_redemption_request(redeem_id)
        if not isinstance(redemp_request, RedemptionRequest):
            return redemp_request

        name = result.get("name")
        value = result.get("value")
        desc = result.get("description")

        if name:
            redemp_request.name = name
        if value:
            redemp_request.value = value
        if desc:
            redemp_request.description = desc

        redemp_request.save()

        return response_builder(dict(
            data=serialize_redmp(redemp_request),
            status="success",
            message="RedemptionRequest edited successfully."
        ), 200)

    @classmethod
    @token_required
    @roles_required(["finance", "cio", "society president", "vice president",
                     "secretary", "success ops"])
    def get(cls, redeem_id=None):
        """Get Redemption Requests."""
        if redeem_id:
            redemp_request = RedemptionRequest.query.get(redeem_id)
            return find_item(redemp_request)
        else:
            search_term_name = request.args.get('society')
            if search_term_name:
                society = Society.query.filter_by(
                    name=search_term_name).first()
                if not society:
                    mes = f"Society with name:{search_term_name} not found"
                    return {"message": mes}, 400
                redemp_request = RedemptionRequest.query.filter_by(
                    society_id=society.uuid)
                return paginate_items(redemp_request)

            search_term_status = request.args.get('status')
            if search_term_status:
                redemp_request = RedemptionRequest.query.filter_by(
                    status=search_term_status)
                return paginate_items(redemp_request)

            search_term_name = request.args.get('name')
            if search_term_name:
                redemp_request = RedemptionRequest.query.filter_by(
                    name=search_term_name)
                return paginate_items(redemp_request)

            search_term_center = request.args.get("center")
            if search_term_center:
                center_query = Center.query.filter_by(
                    name=search_term_center).first()
                if not center_query:
                    mes = f"country with name:{search_term_center} not found"
                    return {"message": mes}, 400

                redemp_request = RedemptionRequest.query.filter_by(
                    center=center_query)
                return paginate_items(redemp_request)

        redemption_requests = RedemptionRequest.query
        return paginate_items(redemption_requests)

    @classmethod
    @token_required
    @roles_required(["success ops", "society president"])
    def delete(cls, redeem_id=None):
        """Delete Redemption Requests."""
        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        redemp_request = get_redemption_request(redeem_id)
        if not isinstance(redemp_request, RedemptionRequest):
            return redemp_request

        redemp_request.delete()
        return response_builder(dict(
            status="success",
            message="RedemptionRequest deleted successfully."), 200)


class RedemptionRequestNumeration(Resource):
    """
    Approve or reject Redemption Requests.

    After approval or rejection the relevant society get the result of the
    request reflects on the amount of points.
    Only done by success ops.
    """

    @classmethod
    @token_required
    @roles_required(["success ops", "cio"])
    def put(cls, redeem_id=None):
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

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                data=None,
                status="fail",
                message="Resource does not exist."
            ), 404)

        status = result.get("status")
        comment = result.get("comment")
        rejection_reason = result.get("rejection")

        if status == "approved":
            user = redemp_request.user
            society = Society.query.get(user.society_id)
            society.used_points = redemp_request
            redemp_request.status = status

            # Get the relevant Finance Center to respond on RedemptionRequest
            if str(redemp_request.center.name.lower()) == 'kampala':
                finance_email = redemp_request.center.name.lower() + \
                    ".finance@andela.com"
            else:
                finance_email = redemp_request.center.name.lower() + \
                    "-finance@andela.com"

            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="Redemption Request on {} has been approved. Click the link below"
                        " <a href='{}'>here</a> to view more details.".format(
                    redemp_request.name, request.host_url + 'api/v1/societies/redeem/' +
                    redeem_id
                ),
                recipients=[finance_email]
            )

            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="Redemption Request on {} has been approved. Finance"
                " will be in touch.".format(redemp_request.name),
                recipients=[redemp_request.user.email]
            )

        elif status == "rejected":
            redemp_request.status = status
            redemp_request.rejection = rejection_reason
            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="This redemption request has been rejected for this"
                        " reason:".format(redemp_request.rejection),
                recipients=[redemp_request.user.email]
            )

        elif comment:
            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="More Info on RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message=comment,
                recipients=[redemp_request.user.email]
            )  # cover for requesting more information

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


class RedemptionRequestFunds(Resource):
    """
    Mark Redemption Requests are complete.

    The Finance Department marks the redemption request as complete once the
    funds have been sent out.
    """

    decorators = [token_required]

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

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                data=None,
                status="fail",
                message="Resource does not exist."
            ), 404)

        status = payload.get("status")

        if status == "completed":
            redemp_request.status = status

            send_email.delay(
                sender=current_app.config["SENDER_CREDS"],
                subject="RedemptionRequest for {}".format(
                    redemp_request.user.society.name),
                message="Redemption Request on {} has been completed. Finance"
                " has wired the money to the reciepient.".format(
                    redemp_request.name),
                recipients=[redemp_request.user.email,
                            current_app.config["CIO"]]
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
