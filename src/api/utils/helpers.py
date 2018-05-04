"""Contain utility functions and constants."""
import datetime
from flask import jsonify, request, current_app, url_for
from collections import namedtuple

from api.models import Activity, ActivityType, Role


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


def paginate_roles():
    """Pagniate all roles for display."""
    _page = request.args.get('page')
    _limit = request.args.get('limit')
    page = int(_page or current_app.config['DEFAULT_PAGE'])
    limit = int(_limit or current_app.config['PAGE_LIMIT'])
    roles = Role.query

    roles = roles.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )
    if roles.items:
        previous_url = None
        next_url = None
        if roles.has_next:
            next_url = url_for(request.endpoint, limit=limit,
                               page=page+1, _external=True)
        if roles.has_prev:
            previous_url = url_for(request.endpoint, limit=limit,
                                   page=page-1, _external=True)

        roles_list = []
        for _role in roles.items:
            role = _role.serialize()
            roles_list.append(role)

        response = jsonify({
            "status": "success",
            "data": {"roles": roles_list,
                     "count": len(roles.items),
                     "nextUrl": next_url,
                     "previousUrl": previous_url,
                     "currentPage": roles.page},
            "message": "Roles fetched successfully."
        })
        response.status_code = 200
        return response
    else:
        response = jsonify({
            "status": "success",
            "data": {"roles": [],
                     "count": 0},
            "message": "There are no roles."
        })
        response.status_code = 404
        return response


def edit_role(payload, search_term):
    """Find and edit the role."""
    role = Role.query.get(search_term)
    name = payload["name"]
    # if edit request == stored value
    if name == role.name:
        response = jsonify({
            "data": {"path": role.serialize()},
            "message": "No change specified."
        })
        response.status_code = 200
        return response
    else:
        if role:
            if name:
                old_role_name = role.name
                role.name = name
            else:
                return {"status": "fail",
                        "message": "Name to edit to"
                                   " must be provided."}, 400
            role.save()
            response = jsonify({
                "data": {"path": role.serialize()},
                "message": "Role {} has been changed"
                           " to {}.".format(old_role_name, role.name)
            })
            response.status_code = 200
        else:
            response = jsonify({"status": "fail",
                                "message": "Role does not exist."})
            response.status_code = 404
        return response


def find_role(role):
    """Find a role within the API."""
    if role:
        response = jsonify({
            "data": role.serialize(),
            "status": "success",
            "message": "Role {} fetched successfully.".format(role.name)
        })
        response.status_code = 200
        # return response
    else:
        response = jsonify({
            "data": None,
            "status": "fail",
            "message": "Specified role does not exist."
        })
        response.status_code = 404
    return response

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
