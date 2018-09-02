from marshmallow import fields, validates_schema, validate, ValidationError

from api.endpoints.users.models import User
from api.endpoints.activity_type.models import ActivityType
from api.utils.marshmallow_schemas import BaseSchema


class LoggedActivitySchema(BaseSchema):
    """Creates a validation schema for logged activities."""

    status = fields.String()
    points = fields.Integer(attribute='value')
    date = fields.Date(attribute='activity_date',
                       dump_to='activityDate', load_from='activityDate')
    owner = fields.String(attribute='user.name')
    owner_photo = fields.Url(attribute='user.photo')
    activity_id = fields.String(dump_to='activityId', load_from='activityId')
    activity = fields.String(attribute='activity.name')
    category = fields.String(attribute='activity_type.name')
    redeemed = fields.Boolean()
    activity_type_id = fields.String(
        load_from='activityTypeId', dump_to='activityTypeId'
    )
    no_of_participants = fields.Integer(load_from='noOfParticipants',
                                        dump_to='noOfParticipants')
    society_id = fields.String(dump_to='societyId', load_from='societyId')
    society = fields.String(attribute='society.name')
    approved_by = fields.Method(
        'get_approver', dump_to='approvedBy', load_from='approvedBy'
    )
    reviewed_by = fields.Method(
        'get_reviewer', dump_to='reviewedBy', load_from='reviewedBy'
    )

    @staticmethod
    def get_approver(obj):
        """Get approver name."""
        if obj.approver_id:
            approver = User.query.get(obj.approver_id)
            return approver.name
        return

    @staticmethod
    def get_reviewer(obj):
        """Get reviewer name."""
        if obj.reviewer_id:
            reviewer = User.query.get(obj.reviewer_id)
            return reviewer.name
        return


class LoggedActivitiesSchema(LoggedActivitySchema):
    date = fields.Date(attribute='activity_date', dump_to='activityDate')
    society = fields.Nested(BaseSchema, only=('uuid', 'name'))
    user = fields.String(attribute='user.name', dump_to='owner')


class LogEditActivitySchema(BaseSchema):
    """Validation Schema for LoggedActivity."""

    name = fields.String(required=False)
    activity_id = fields.String(
        validate=[validate.Length(max=36)], load_from='activityId'
    )
    activity_type_id = fields.String(
        validate=[validate.Length(max=36)], load_from='activityTypeId', required=False
    )
    date = fields.Date()
    no_of_participants = fields.Integer(load_from='noOfParticipants')

    @validates_schema
    def validate_logged_activity(self, data):
        """Validate the logged activity."""
        if not self.context.get('edit'):
            if (data.get('activity_type_id') and data.get('activity_id')) or not \
                    data.get('activity_type_id') and not data.get('activity_id'):
                raise ValidationError(
                    'Please send either an activityTypeId or an activityId only',
                    'error'
                )

        if data.get('activity_type_id') and not (data.get('date') and
                                                 data.get('description')):
            raise ValidationError(
                'Please send a date and description', 'error'
            )

        # NOTE: The following part allows for users to log their own
        # activities when an activity has not been added by an
        # authorized person. When adding activities for hackathons,
        # bootcamps, tech events etc is made a requirement, it should
        # be removed so that only supported activity types are logged
        # via activity_type_id
        multi_participant_activities = [x.uuid for x in ActivityType.query.filter_by(
            supports_multiple_participants=True).all()]
        if data.get('activity_type_id') in multi_participant_activities \
                and not data.get('no_of_participants'):
            raise ValidationError(
                'Please send all required fields for this activity'
                ' i.e. a date, number of participants and a description',
                'no_of_participants'
            )


single_logged_activity_schema = LoggedActivitySchema()
user_logged_activities_schema = LoggedActivitySchema(
    many=True, exclude=('society', 'society_id')
)
logged_activities_schema = LoggedActivitiesSchema(many=True)
