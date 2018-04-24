"""Validation schemas."""
from datetime import date
from marshmallow import (Schema, fields, post_load, validates,
                         validate, ValidationError)
from api.models import User, Activity, ActivityType, Role


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
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    description = fields.String()


class RoleSchema(BaseSchema):
    """Creates a Validation schema for Roles."""

    @post_load
    def verify_role(self, data):
        """Extra validation for Roles."""
        existing_role = Role.query.filter(
                        Role.name.ilike(data['name'])).first()

        if existing_role:
            self.context = {'status_code': 409}
            raise ValidationError({'name': 'Role already exists!'})


class ActivityTypesSchema(BaseSchema):
    """Creates a validation schema for activity types."""

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


class LoggedActivitySchema(BaseSchema):
    """Creates a validation schema for logged activities."""

    status = fields.String()
    points = fields.Integer(attribute='value')
    date = fields.Date(attribute='activity_date')
    user = fields.String(attribute='user.name')
    activity_id = fields.String()
    activity = fields.String(attribute='activity.name')
    category = fields.String(attribute='activity_type.name')
    redeemed = fields.Boolean()
    activity_type_id = fields.String()
    society_id = fields.String()
    society = fields.String(attribute='society.name')
    approved_by = fields.Method('get_approver')

    @staticmethod
    def get_approver(obj):
        """Get approver details."""
        if obj.approver_id:
            approver = User.query.get(obj.approver_id)
            return approver.name
        return


class ActivitySchema(BaseSchema):
    """Creates a validation schema for activities."""

    description = fields.String(
        required=True,
        error_messages={
            'required': {'message': 'A description is required.'}
        })
    activity_type_id = fields.String(
        required=True,
        validate=validate.Length(equal=36,
                                 error='The id provided is not valid.'),
        error_messages={
            'required': {'message': 'An activity type ID is required.'}
        })
    activity_date = fields.Date(
        required=True,
        error_messages={
                'required': {'message': 'An activity date is required.'}
        })
    added_by_id = fields.String(dump_only=True)

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


activity_types_schema = ActivityTypesSchema(many=True)
user_logged_activities_schema = LoggedActivitySchema(
    many=True, exclude=('society', 'society_id')
)
activity_schema = ActivitySchema()
role_schema = RoleSchema()
