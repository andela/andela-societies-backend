"""Validation schemas."""

from marshmallow import (Schema, fields, validate)


class BaseSchema(Schema):
    """Creates a base validation schema."""

    uuid = fields.String(dump_only=True, dump_to='id',
                         validate=[validate.Length(max=36)])
    name = fields.String(
        required=True,
        error_messages={
            'required': {'message': 'A name is required.'}
        })
    photo = fields.String()
    email = fields.String()
    created_at = fields.DateTime(
        dump_only=True, dump_to='createdAt', load_from='createdAt'
    )
    modified_at = fields.DateTime(
        dump_only=True, dump_to='modifiedAt', load_from='modifiedAt'
    )
    description = fields.String()


basic_info_schema = BaseSchema()
