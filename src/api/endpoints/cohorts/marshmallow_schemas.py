from marshmallow import fields, validate

from api.utils.marshmallow_schemas import BaseSchema


class CohortSchema(BaseSchema):
    """Validation Schema for Cohort."""

    center_id = fields.String(dump_only=True, dump_to='centerId',
                              validate=[validate.Length(max=36)])
    society_id = fields.String(dump_only=True, dump_to='societyId',
                               validate=[validate.Length(max=36)])


cohort_schema = CohortSchema()
