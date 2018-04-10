"""Contain utility functions and constants."""
import datetime
from collections import namedtuple

from api.models import Activity, ActivityType


ParsedResult = namedtuple(
        'ParsedResult',
        ['activity', 'activity_type', 'activity_date', 'activity_value']
    )


def parse_log_activity_fields(result):
    if result.get('activity_id'):
        activity = Activity.query.get(result['activity_id'])
        if not activity:
            return dict(message='Invalid activity id'), 422

        activity_type = activity.activity_type
        if activity_type.name == 'Bootcamp Interviews' and \
                not (result.get('no_of_interviewees')
                        and result.get('description')):
            return dict(
                message='Please send the number of interviewees and' \
                ' their names in the description'
            ), 400

        activity_date = activity.activity_date
        time_difference = datetime.date.today() - activity_date
    else:
        activity_date = result['date']
        if activity_date > datetime.date.today():
            return dict(message='Invalid activity date'), 422

        activity_type = ActivityType.query.get(
            result['activity_type_id']
        )
        if not activity_type:
            return dict(message='Invalid activity type id'), 422
        activity = None
        time_difference = datetime.date.today() - activity_date


    if time_difference.days > 30:
        return dict(
            message = 'You\'re late. That activity' \
            ' happened more than 30 days ago'
        ), 422

    activity_value = activity_type.value if not \
        activity_type.name == 'Bootcamp Interviews' else \
        activity_type.value * result['no_of_interviewees']

    return ParsedResult(
        activity, activity_type, activity_date, activity_value
    )


# def serialize_point(point):
#     """Map point object to dict representation.

#     Args:
#        point(Point): point object

#     Returns:
#        serialized_point(dict): dict representation of point
#     """
#     serialized_point = point.serialize()
#     serialized_point["id"] = serialized_point.pop("uuid")
#     serialized_point["activity"] = point.activity.name
#     serialized_point["owner"] = point.user.name

#     return serialized_point
