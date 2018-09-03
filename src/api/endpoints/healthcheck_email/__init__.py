"""Setup Email Healthcheck resource blueprint."""


def email_healthcheck_bp(Api, Blueprint):
    from .healthcheck_email import NotificationsAPI

    email_healthcheck_service = Blueprint('email_healthcheck', __name__)
    email_healthcheck_api = Api(email_healthcheck_service)

    # activities endpoints
    email_healthcheck_api.add_resource(
        NotificationsAPI, "/api/v1/health/email",
        "/api/v1/health/email/",
        endpoint="email_healthcheck"
    )
    return email_healthcheck_service
