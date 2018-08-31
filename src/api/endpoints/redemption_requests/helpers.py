from flask import g

from api.endpoints.societies.models import Society
from api.utils.helpers import response_builder
from api.utils.marshmallow_schemas import basic_info_schema


from .marshmallow_schemas import redemption_schema
from .models import RedemptionRequest


def get_redemption_request(redeem_id):
    if "society president" in [role.name for role in g.current_user.roles]:
        redemp_request = g.current_user.society.redemptions.filter_by(
            uuid=redeem_id).one_or_none()
    else:
        redemp_request = RedemptionRequest.query.get(redeem_id)
    if not redemp_request:
        return response_builder(dict(
            status="fail",
            message="RedemptionRequest does not exist."),
            404)

    if redemp_request.status != "pending":
        return response_builder(dict(
            status="fail",
            message="RedemptionRequest already approved or rejected"), 403)

    return redemp_request


def serialize_redmp(redemption):
    """To serialize and package redeptions."""
    serial_data, _ = redemption_schema.dump(redemption)
    seriallized_user, _ = basic_info_schema.dump(redemption.user)
    serilaized_society, _ = basic_info_schema.dump(
        Society.query.get(redemption.user.society_id))
    serial_data["user"] = seriallized_user
    serial_data["society"] = serilaized_society
    serial_data["center"], _ = basic_info_schema.dump(redemption.center)
    return serial_data
