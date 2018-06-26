"""RedemptionRequest Module."""

from flask import request, g
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.utils.helpers import find_item, paginate_items, response_builder
from ..models import Society, RedemptionRequest, User, Country


class PointRedemptionAPI(Resource):
    """
    Resource handling all point redemption requests.

    Only made by society presidents.
    """

    @classmethod
    @token_required
    @roles_required(["Society President"])
    def post(cls):
        """Create Redemption Request."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Redemption request must have data.",
                status="fail"
            ), 400)

        name = payload.get("name")
        value = payload.get("value")
        country_input = payload.get("country")

        country = Country.query.filter_by(name=country_input).first()

        if name and value and country_input:
            redemp_request = RedemptionRequest(
                name=name,
                value=value,
                user=g.current_user,
                country=country
            )

            redemp_request.save()

            return response_builder(dict(
                message="Redemption request created. Success Ops will be in"
                        " touch soon.",
                status="success",
                data=redemp_request.serialize()
            ), 201)

        else:
            return response_builder(dict(
                message="Redemption request name, value and country required",
                status="fail"
            ), 400)

    @classmethod
    @token_required
    @roles_required(["Society President", "Success Ops"])
    def put(cls, redeem_id=None):
        """Edit Redemption Requests."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="Redemption Request to be edited must be provided"),
                400)

        redemp_request = RedemptionRequest.query.filter_by(
                            uuid=redeem_id).first()
        if not redemp_request:
            return response_builder(dict(
                                status="fail",
                                message="RedemptionRequest does not exist."),
                                404)

        name = payload.get("name")
        value = payload.get("value")
        desc = payload.get("description")

        if name:
            redemp_request.name = name
        if value:
            redemp_request.value = value
        if desc:
            redemp_request.description = desc

        redemp_request.save()

        return response_builder(dict(
            data=redemp_request.serialize(),
            status="success",
            message="RedemptionRequest edited successfully."
        ), 200)

    @classmethod
    @token_required
    @roles_required(["CIO", "President", "Vice President", "Secretary"])
    def get(cls, redeem_id=None):
        """Get Redemption Requests."""
        if redeem_id:
            redemp_request = RedemptionRequest.query.get(redeem_id)
            return find_item(redemp_request)
        else:
            search_term_name = request.args.get('name')
            if search_term_name:
                redemp_request = RedemptionRequest.query.filter_by(
                                        name=search_term_name).first()
                return find_item(redemp_request)

            search_term_status = request.args.get('status')
            if search_term_status:
                redemp_request = RedemptionRequest.query.filter_by(
                                        status=search_term_status)
                return paginate_items(redemp_request)

            search_term_society = request.args.get('society')
            if search_term_society:
                society_query = Society.query.filter_by(
                                name=search_term_society).first()
                if not society_query:
                    return response_builder(dict(
                        status="success",
                        data=dict(data_list=[],
                                  count=0),
                        message="Resources were not found."
                    ), 404)

                redemp_request = (
                    RedemptionRequest.query.join(User,
                                                 RedemptionRequest.user).filter(
                                        User.society_id ==
                                        society_query.uuid
                                        ))
                return paginate_items(redemp_request)

            search_term_country = request.args.get("country")
            if search_term_country:
                country_query = Country.query.filter_by(
                            name=search_term_country).first()

                redemp_request = RedemptionRequest.query.filter_by(
                                        country=country_query)
                return paginate_items(redemp_request)

        redemption_requests = RedemptionRequest.query
        return paginate_items(redemption_requests)

    @classmethod
    @token_required
    @roles_required(["Success Ops", "Society President"])
    def delete(cls, redeem_id=None):
        """Delete Redemption Requests."""
        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest does not exist."), 404)

        redemp_request.delete()
        return response_builder(dict(
                status="success",
                message="RedemptionRequest deleted successfully."), 200)


class PointRedemptionRequestNumeration(Resource):
    """
    Approve or reject Redemption Requests.

    After approval or rejection the relevant society get the result of the
    request reflects on the amount of points.
    Only done by Success Ops.
    """

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls, redeem_id=None):
        """Approve or Reject Redemption requests."""
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

        try:
            status = payload["status"]
        except KeyError as e:
            return response_builder(dict(
                module="RedemptionRequest Module",
                errors=e,
                message="Missing fields"), 400)

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                data=None,
                status="fail",
                message="Resource does not exist."
            ), 404)

        if status == "approved":
            user = redemp_request.user
            society = Society.query.get(user.society_id)
            society.used_points = redemp_request
            redemp_request.status = status
        else:
            redemp_request.status = status

        return response_builder(dict(
            message="RedemptionRequest status changed to {}".format(
                                                        redemp_request.status),
            status="success",
            data=redemp_request.serialize()
        ), 200)
