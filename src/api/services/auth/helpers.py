import os

import requests
from flask import jsonify

from api.models import Role, User, Center, Cohort


def add_extra_user_info(token,
                        user_id,
                        url=os.environ.get(
                            'ANDELA_API_URL'
                        )):  # pragma: no cover
    """Retrive user information from ANDELA API.

    params:
        token(str): valid jwt token
        user_id(str): id for user to retive information about

    Return:
        tuple(location, cohort, api_response)
    """
    cohort = location = None
    Bearer = 'Bearer '
    headers = {'Authorization': Bearer + token}

    try:
        api_response = requests.get(url + f"users/{user_id}", headers=headers)
    except requests.exceptions.ConnectionError:
        response = jsonify({"Error": "Network Error."})
        response.status_code = 503
        return cohort, location, response
    except Exception:
        response = jsonify({"Error": "Something went wrong."})
        response.status_code = 500
        return cohort, location, response

    if api_response.status_code == 200 and api_response.json().get('cohort'):
        cohort = Cohort.query.filter_by(
            uuid=api_response.json().get('cohort').get('id')).first()
        if not cohort:
            cohort = Cohort(uuid=api_response.json().get('cohort').get('id'),
                            name=api_response.json().get('cohort').get('name'))

        location = Center.query.filter_by(
            uuid=api_response.json().get('location').get('id')).first()
        if not location:
            location = Center(
                uuid=api_response.json().get('location').get('id'))
    return cohort, location, api_response


def store_user_details(payload, token):
    """Store user details in our database."""
    user_id = payload["UserInfo"]["id"]
    name = payload["UserInfo"]["name"]
    email = payload["UserInfo"]["email"]
    photo = payload["UserInfo"]["picture"]
    roles = payload["UserInfo"]["roles"]

    user = User.query.get(user_id)
    print("this is the new print", user)
    # save user to db if they haven't been saved yet
    if not user:
        user = User(
            uuid=user_id, name=name, email=email, photo=photo
        )

    cohort, location, _ = add_extra_user_info(token, user_id)

    if cohort:
        cohort.members.append(user)
        cohort.save()
        user.society_id = cohort.society.uuid if cohort.society else None
    if location:
        location.members.append(user)
        location.save()

    # set users roles
    user.roles = [
        Role.query.filter_by(name=role.lower()).first() for role in roles
        if role and role != "Andelan" and Role.query.filter_by(
            name=role.lower()).first() is not None
    ]

    # default to fellow
    user.roles = user.roles if user.roles else [
        Role.query.filter_by(name='fellow').first()
    ]

    user.save()
    return user
