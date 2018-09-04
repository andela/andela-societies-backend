from marshmallow import fields

from api.utils.marshmallow_schemas import BaseSchema


class SocietySchema(BaseSchema):
    """Validation/Serialize Schema for Society."""

    _total_points = fields.Integer(dump_only=True, dump_to='totalPoints')
    _used_points = fields.Integer(dump_only=True, dump_to='usedPoints')
    remaining_points = fields.Integer(dump_only=True, dump_to='remainingPoints')
    color_scheme = fields.String(dump_only=True, dump_to='colorScheme')


society_schema = SocietySchema()
