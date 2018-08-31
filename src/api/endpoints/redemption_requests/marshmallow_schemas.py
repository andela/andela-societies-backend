from api.utils.marshmallow_schemas import BaseSchema
from marshmallow import fields


class RedemptionRequestSchema(BaseSchema):
    """RedemptionRequest serializer/validator."""

    name = fields.String(
        load_from='reason',
        required=True,
        error_messages={
            'required': {'message': 'A reason is required.'}
        })
    value = fields.Integer(
        load_from='points',
        required=True,
        error_messages={
            'required': {'message': 'A value is required.'}
        })
    center = fields.String(
        required=True,
        error_messages={
            'required': {'message': 'Center name is required.'}
        })


class EditRedemptionRequestSchema(BaseSchema):
    """Edit RedemptionRequest validator."""

    name = fields.String()
    value = fields.Integer()
    status = fields.String()
    comment = fields.String()
    rejection_reason = fields.String(load_from='rejection')


class RedemptionSchema(BaseSchema):
    """Redemption serializer/validator."""

    status = fields.String(dump_only=True)
    value = fields.Integer(dump_only=True)


redemption_request_schema = RedemptionRequestSchema()
edit_redemption_request_schema = EditRedemptionRequestSchema()
redemption_schema = RedemptionSchema()
