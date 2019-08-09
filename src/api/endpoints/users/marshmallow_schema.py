from marshmallow import fields, validate

from api.utils.marshmallow_schemas import BaseSchema


class UserSchema(BaseSchema):
    """User serializer/validator."""

    society_id = fields.String(dump_only=True, dump_to='societyId',
                               validate=[validate.Length(max=36)])
    center_id = fields.String(dump_only=True, dump_to='centerId',
                              validate=[validate.Length(max=36)])
    cohort_id = fields.String(dump_only=True, dump_to='cohortId',
                              validate=[validate.Length(max=36)])


users_schema = UserSchema(many=True)
user_schema = UserSchema()
