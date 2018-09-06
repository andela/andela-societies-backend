from marshmallow import fields

from api.utils.marshmallow_schemas import BaseSchema


class EmailValidator(BaseSchema):
    """Validation for email."""

    recipient = fields.Email(
        required=True,
        error_messages={
            'message': 'Please send the activity points value'
        }
    )


email_schema = EmailValidator()
