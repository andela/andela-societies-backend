from datetime import date
from marshmallow import (ValidationError, fields, post_load, validate,
                         validates)

from api.utils.marshmallow_schemas import BaseSchema
from api.models import ActivityType

from .models import Activity


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


activity_schema = ActivitySchema()
