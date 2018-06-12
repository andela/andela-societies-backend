"""Contain utility functions and constants."""
import datetime
import requests
import os
from collections import namedtuple
from flask import jsonify, request, current_app, url_for, Response

from api.models import Activity, ActivityType, Cohort, Country, Role


ParsedResult = namedtuple(
        'ParsedResult',
        ['activity', 'activity_type', 'activity_date', 'activity_value']
    )


def parse_log_activity_fields(result):
    """Parse the fields of the Log Activity Fields."""
    if result.get('activity_id'):
        activity = Activity.query.get(result['activity_id'])
        if not activity:
            return response_builder(dict(message='Invalid activity id'), 422)

        activity_type = activity.activity_type
        if activity_type.name == 'Bootcamp Interviews' and \
                not (result.get('no_of_interviewees')
                     and result.get('description')):
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

        activity_type = ActivityType.query.get(
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
        activity_type.name == 'Bootcamp Interviews' else \
        activity_type.value * result['no_of_interviewees']

    return ParsedResult(
        activity, activity_type, activity_date, activity_value
    )


def paginate_items(fetched_data):
    """Pagniate all roles for display."""
    _page = request.args.get('page')
    _limit = request.args.get('limit')
    page = int(_page or current_app.config['DEFAULT_PAGE'])
    limit = int(_limit or current_app.config['PAGE_LIMIT'])

    fetched_data = fetched_data.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )
    if fetched_data.items:
        previous_url = None
        next_url = None

        if fetched_data.has_next:
            next_url = url_for(request.endpoint, limit=limit,
                               page=page+1, _external=True)
        if fetched_data.has_prev:
            previous_url = url_for(request.endpoint, limit=limit,
                                   page=page-1, _external=True)

        data_list = []
        for _fetched_item in fetched_data.items:
            data_item = _fetched_item.serialize()
            data_list.append(data_item)

        return response_builder(dict(
            status="success",
            data=dict(data_items=data_list,
                      count=len(fetched_data.items),
                      nextUrl=next_url,
                      previousUrl=previous_url,
                      currentPage=fetched_data.page),
            message="Data fetched successfully."
        ), 200)

    return response_builder(dict(
        status="success",
        data=dict(data_list=[],
                  count=0),
        message="Resources were not found."
    ), 404)


def edit_role(payload, search_term):
    """Find and edit the role."""
    role = Role.query.get(search_term)
    # if edit request == stored value
    if not role:
        return response_builder(dict(status="fail",
                                     message="Role does not exist."), 404)

    try:
        if payload["name"] == role.name:
            return response_builder(dict(
                data=dict(path=role.serialize()),
                message="No change specified."
            ), 200)

        else:
            old_role_name = role.name
            role.name = payload["name"]
            role.save()

            return response_builder(dict(
                data=dict(path=role.serialize()),
                message="Role {} has been changed"
                        " to {}.".format(old_role_name, role.name)
            ), 200)

    except KeyError:
        return response_builder(
            dict(status="fail",
                 message="Name to edit to must be provided."), 400)


def find_item(data):
    """Build the response with found/404 item in DB."""
    if data:
        return response_builder(dict(
            data=data.serialize(),
            status="success",
            message="{} fetched successfully.".format(data.name)
        ), 200)

    return response_builder(dict(
        data=None,
        status="fail",
        message="Resource does not exist."
    ), 404)


def response_builder(data, status_code=200):
    """Build the jsonified response to return."""
    response = jsonify(data)
    response.status_code = status_code
    return response


def add_extra_user_info(token, user_id, url=os.environ.get('ANDELA_API_URL')):
    """Retrive user information from ANDELA API.

    params:
        token(str): valid jwt token
        user_id(str): id for user to retive information about

    returns: tuple(location, cohort, api_response)
    """
    cohort = location = None
    Bearer = 'Bearer '
    headers = {'Authorization': Bearer + token}

    try:
        api_response = requests.get(url + f"users/{user_id}", headers=headers)
    except requests.exceptions.ConnectionError:
        response = Response()
        response.status_code = 503
        response.json = lambda: {"Error": "Network Error."}
        return cohort, location, response
    except Exception:
        response = Response()
        response.status_code = 500
        response.json = lambda: {"Error": "Something went wrong."}
        return cohort, location, response

    if api_response.status_code == 200 and api_response.json().get('cohort'):
        cohort = Cohort.query.filter_by(
            uuid=api_response.json().get('cohort').get('id')).first()
        if not cohort:
            cohort = Cohort(uuid=api_response.json().get('cohort').get('id'),
                            name=api_response.json().get('cohort').get('name'))

        location = Country.query.filter_by(
            uuid=api_response.json().get('location').get('id')).first()
        if not location:
            location = Country(
                    uuid=api_response.json().get('location').get('id'))
    return cohort, location, api_response
