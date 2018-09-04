import datetime
from collections import namedtuple

from api.utils.helpers import response_builder


ParsedResult = namedtuple(
    'ParsedResult',
    ['activity', 'activity_type', 'activity_date', 'activity_value']
)


def parse_log_activity_fields(result, activity_model, activity_type_model):
    """Parse the fields of the Log Activity Fields."""
    if result.get('activity_id'):
        activity = activity_model.query.get(result['activity_id'])
        if not activity:
            return response_builder(dict(message='Invalid activity id'), 422)

        activity_type = activity.activity_type
        if activity_type.supports_multiple_participants and \
                not (result.get('no_of_participants') and
                     result.get('description')):
            return response_builder(dict(
                message='Please send the number of interviewees and'
                ' their names in the description'
            ), 400)

        activity_date = activity.activity_date
        time_difference = datetime.date.today() - activity_date
    else:
        activity_date = result['date']
        if activity_date > datetime.date.today():
            return response_builder(dict(message='Invalid activity date'), 422)

        activity_type = activity_type_model.query.get(
            result['activity_type_id']
        )
        if not activity_type:
            return response_builder(dict(message='Invalid activity type id'),
                                    422)
        activity = None
        time_difference = datetime.date.today() - activity_date

    if time_difference.days > 30:
        return response_builder(dict(
            message='You\'re late. That activity'
            ' happened more than 30 days ago'
        ), 422)

    activity_value = activity_type.value if not \
        activity_type.supports_multiple_participants else \
        activity_type.value * result['no_of_participants']

    return ParsedResult(
        activity, activity_type, activity_date, activity_value
    )
