"""Validation schemas."""
from datetime import date

from marshmallow import (Schema, ValidationError, fields, post_load, validate,
                         validates, validates_schema)

from api.models import Activity, ActivityType, Role, User


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
    created_at = fields.DateTime(
        dump_only=True, dump_to='createdAt', load_from='createdAt'
    )
    modified_at = fields.DateTime(
        dump_only=True, dump_to='modifiedAt', load_from='modifiedAt'
    )
    description = fields.String()


class RoleSchema(BaseSchema):
    """Create a validation schema for Roles."""

    @post_load
    def verify_role(self, data):
        """Extra validation of roles."""
        existing_role = Role.query.filter(
            Role.name.ilike(data['name'])).first()

        if existing_role:
            self.context = {'status_code': 409}
            raise ValidationError({'message': 'Role already exists!'})


class ActivityTypesSchema(BaseSchema):
    """Creates a validation schema for activity types."""

    description = fields.String(
        required=True,
        error_messages={
            'message': 'A description is required.'
        }
    )
    value = fields.Integer(
        required=True,
        error_messages={
            'message': 'Please send the activity points value'
        }
    )

    supports_multiple_participants = fields.Boolean(
        error_messages={
            'message': 'Please send value if activity supports multiple participants'
        },
        dump_to='supportsMultipleParticipants'
    )

    @post_load
    def verify_activity_type(self, data):
        """Extra validation of activity type."""
        existing_activity_type_name = ActivityType.query.filter(
            ActivityType.name.ilike(data['name'])).first()

        if existing_activity_type_name:
            self.context = {'status_code': 409}
            raise ValidationError({'message':
                                   'Activity Type (name) already exists!'})


class ActivitySchema(BaseSchema):
    """Creates a validation schema for activities."""

    description = fields.String(
        required=True,
        error_messages={
            'required': {'message': 'A description is required.'}
        })
    activity_type_id = fields.String(
        required=True, load_from='activityTypeId', dump_to='activityTypeId',
        validate=validate.Length(equal=36,
                                 error='The id provided is not valid.'),
        error_messages={
            'required': {'message': 'An activity type ID is required.'}
        })
    activity_date = fields.Date(
        required=True, dump_to='activityDate', load_from='activityDate',
        error_messages={
            'required': {'message': 'An activity date is required.'}
        })
    added_by_id = fields.String(
        dump_only=True, dump_to='addedById', load_from='addedById'
    )

    @post_load
    def verify_activity(self, data):
        """Extra validation for the Activity Schema."""
        invalid_activity_names = ['Blog', 'App', 'Open Source']
        activity_type = ActivityType.query.get(data['activity_type_id'])
        existing_activity = Activity.query.filter(
            Activity.name.ilike(data['name'])).first()

        if not activity_type or activity_type.name in invalid_activity_names:
            self.context = {'status_code': 404}
            raise ValidationError(
                {'activity_type_id':
                 'Activity type does not exist or is unsupported.'})

        if existing_activity:
            self.context = {'status_code': 409}
            raise ValidationError({'name': 'Activity already exists!'})

        if any(name in data['name'] for name in invalid_activity_names):
            raise ValidationError({'name': 'This is not a valid activity!'})

    @validates('activity_date')
    def validates_activity_date(self, value):
        """Validate the activity date field."""
        if value < date.today():
            raise ValidationError(
                {'message':
                 'Date is in the past! Please enter a valid date.'})
        else:
            return value


class UserSchema(BaseSchema):
    """User serializer/validator."""

    society_id = fields.String(dump_only=True, dump_to='societyId',
                               validate=[validate.Length(max=36)])
    center_id = fields.String(dump_only=True, dump_to='centerId',
                              validate=[validate.Length(max=36)])
    cohort_id = fields.String(dump_only=True, dump_to='cohortId',
                              validate=[validate.Length(max=36)])


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


activity_types_schema = ActivityTypesSchema(many=True)
new_activity_type_schema = ActivityTypesSchema()
activity_schema = ActivitySchema()

role_schema = RoleSchema()
base_schema = BaseSchema()
user_schema = UserSchema()
basic_info_schema = BaseSchema()
redemption_request_schema = RedemptionRequestSchema()
edit_redemption_request_schema = EditRedemptionRequestSchema()
redemption_schema = RedemptionSchema()
