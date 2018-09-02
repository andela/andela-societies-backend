"""setup redemption request resource blueprint."""


def redemption_bp(Api, Blueprint):
    from api.endpoints.societies.models import Society
    from api.models import Center
    from .models import RedemptionRequest
    from .redemption_points import PointRedemptionAPI
    from .redemption_numeration import RedemptionRequestNumeration
    from .redemption_request_funds import RedemptionRequestFunds

    redemption_bp_service = Blueprint('redemption_api', __name__)
    redemption_api = Api(redemption_bp_service)

    redemption_api.add_resource(
        PointRedemptionAPI,
        "/api/v1/societies/redeem/<string:redeem_id>",
        "/api/v1/societies/redeem/<string:redeem_id>/",
        "/api/v1/societies/redeem",
        "/api/v1/societies/redeem/",
        endpoint="point_redemption_detail",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest,
            'Center': Center,
            'Society': Society
            }
    )

    redemption_api.add_resource(
        RedemptionRequestNumeration,
        "/api/v1/societies/redeem/verify/<string:redeem_id>",
        "/api/v1/societies/redeem/verify/<string:redeem_id>/",
        endpoint="redemption_numeration",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest,
            'Society': Society
            }
    )

    redemption_api.add_resource(
        RedemptionRequestFunds,
        "/api/v1/societies/redeem/funds/<string:redeem_id>",
        "/api/v1/societies/redeem/funds/<string:redeem_id>/",
        endpoint="redemption_request_funds",
        resource_class_kwargs={
            'RedemptionRequest': RedemptionRequest
        }
    )
    return redemption_bp_service
