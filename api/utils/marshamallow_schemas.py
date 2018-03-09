from marshmallow import Schema, fields, validate


class BaseSchema(Schema):
    uuid = fields.String(dump_only=True, validate=[
        validate.Length(max=36)])
    name = fields.String(required=True)
    photo = fields.String()
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    description = fields.String()


class ActivityTypesSchema(BaseSchema):
    description = fields.String(
        required=True,
        error_messages={
            'required': 'A description is required.'
            }
    )
    value = fields.Integer(
        required=True,
        error_messages={
            'required': 'Please send the activity points value'
            }
    )


get_activity_types_schema = ActivityTypesSchema(many=True)
