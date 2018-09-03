# system imports
from flask import request, g, current_app
from flask_restful import Resource

# from other packages
from api.services.notifications.tasks import send_email
from api.utils.helpers import find_item, paginate_items, response_builder
from api.services.auth import token_required, roles_required
from api.utils.marshmallow_schemas import basic_info_schema

# from within this package
from .marshmallow_schemas import (
    redemption_schema,
    redemption_request_schema,
    edit_redemption_request_schema)
from .helpers import serialize_redmp, get_redemption_request


class PointRedemptionAPI(Resource):
    """Resource handling all point redemption requests.

    Only made by society presidents.
    """

    def __init__(self, **kwargs):
        """Inject dependacy for resource."""
        self.RedemptionRequest = kwargs['RedemptionRequest']
        self.Center = kwargs['Center']
        self.Society = kwargs['Society']

    @token_required
    @roles_required(["society president"])
    def post(self):
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

        center = self.Center.query.filter_by(name=result.get('center')).first()

        if center:
            redemp_request = self.RedemptionRequest(
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

    @token_required
    @roles_required(["society president", "success ops"])
    def put(self, redeem_id=None):
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
        if not isinstance(redemp_request, self.RedemptionRequest):
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

    @token_required
    @roles_required(["finance", "cio", "society president", "vice president",
                     "secretary, success ops"])
    def get(self, redeem_id=None):
        """Get Redemption Requests."""
        if redeem_id:
            redemp_request = self.RedemptionRequest.query.get(redeem_id)
            return find_item(redemp_request)
        else:
            search_term_name = request.args.get('society')
            if search_term_name:
                society = self.Society.query.filter_by(
                    name=search_term_name).first()
                if not society:
                    mes = f"Society with name:{search_term_name} not found"
                    return {"message": mes}, 400
                redemp_request = self.RedemptionRequest.query.filter_by(
                    society_id=society.uuid)
                return paginate_items(redemp_request)

            search_term_status = request.args.get('status')
            if search_term_status:
                redemp_request = self.RedemptionRequest.query.filter_by(
                    status=search_term_status)
                return paginate_items(redemp_request)

            search_term_name = request.args.get('name')
            if search_term_name:
                redemp_request = self.RedemptionRequest.query.filter_by(
                    name=search_term_name)
                return paginate_items(redemp_request)

            search_term_center = request.args.get("center")
            if search_term_center:
                center_query = self.Center.query.filter_by(
                    name=search_term_center).first()
                if not center_query:
                    mes = f"country with name:{search_term_center} not found"
                    return {"message": mes}, 400

                redemp_request = self.RedemptionRequest.query.filter_by(
                    center=center_query)
                return paginate_items(redemp_request)

        redemption_requests = self.RedemptionRequest.query
        return paginate_items(redemption_requests)

    @token_required
    @roles_required(["success ops", "society president"])
    def delete(self, redeem_id=None):
        """Delete Redemption Requests."""
        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        redemp_request = get_redemption_request(redeem_id)
        if not isinstance(redemp_request, self.RedemptionRequest):
            return redemp_request

        redemp_request.delete()
        return response_builder(dict(
            status="success",
            message="RedemptionRequest deleted successfully."), 200)
