"""setup redemption request resource blueprint."""


def redemption_bp(Api, Blueprint, emit_email_event, mail):
    from api.models import Center, Society
    from .models import RedemptionRequest
    from .redemption_points import PointRedemptionAPI
    from .redemption_numeration import RedemptionRequestNumeration
    from .redemption_request_funds import RedemptionRequestFunds

    redemption_bp_service = Blueprint('redemption_api', __name__)
    redemption_api = Api(redemption_bp_service)

    redemption_api.add_resource(
        PointRedemptionAPI,
        "/societies/redeem/<string:redeem_id>",
        "/societies/redeem/<string:redeem_id>/",
        "/societies/redeem",
        "/societies/redeem/",
        endpoint="point_redemption_detail",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest,
            'Center': Center,
            'Society': Society,
            'email': emit_email_event,
            'mail': mail
        }
    )

    redemption_api.add_resource(
        RedemptionRequestNumeration,
        "/societies/redeem/verify/<string:redeem_id>",
        "/societies/redeem/verify/<string:redeem_id>/",
        endpoint="redemption_numeration",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest,
            'Society': Society,
            'email': emit_email_event,
            'mail': mail
        }
    )

    redemption_api.add_resource(
        RedemptionRequestFunds,
        "/societies/redeem/funds/<string:redeem_id>",
        "/societies/redeem/funds/<string:redeem_id>/",
        endpoint="redemption_request_funds",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest,
            'email': emit_email_event,
            'mail': mail
        }
    )
    return redemption_bp_service
