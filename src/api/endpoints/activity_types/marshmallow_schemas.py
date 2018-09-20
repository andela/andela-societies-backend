from marshmallow import ValidationError, fields, post_load
from api.utils.marshmallow_schemas import BaseSchema

from .models import ActivityType


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
            'message': 'Please send value if activity supports multiple '
            'participants'
        },
        dump_to='supportsMultipleParticipants',
        load_from='supports_multiple'
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


class EditActivityTypesSchema(ActivityTypesSchema):
    """Edit ActivityType validation schema."""

    @post_load
    def verify_activity_type(self, data):
        pass


activity_types_schema = ActivityTypesSchema(many=True)
new_activity_type_schema = ActivityTypesSchema()
edit_activity_type_schema = EditActivityTypesSchema()
