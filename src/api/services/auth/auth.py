"""
Authorisation Module.

This module contains the authorisation required by the client to
communicate with the API.
"""

import base64
import os
from functools import wraps
import requests
from flask import current_app, g, jsonify, request, Response
from jose import ExpiredSignatureError, JWTError, jwt

from api.endpoints.users.models import User
from api.endpoints.roles.models import Role
from api.endpoints.cohorts.models import Cohort
from api.models import Center
from api.utils.helpers import response_builder


def auth_response(status_code, message):
    """Build authentication responses."""
    response = jsonify({
        "message": message
    })
    response.status_code = status_code
    return response


def add_extra_user_info(
    token,
    user_id,
    url=os.environ.get('ANDELA_API_URL')
):  # pragma: no cover
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

    # set current user in flask global variable, g
    user.roles = [
        Role.query.filter_by(name=role.lower()).first() for role in roles
        if role and role != "Andelan" and Role.query.filter_by(
            name=role.lower()).first() is not None]
    user.save()
    return user


def verify_token(authorization_token, public_key, audience=None, issuer=None):
    """Validate token."""
    try:
        payload = jwt.decode(
            authorization_token,
            public_key,
            algorithms=['RS256'],
            options={
                'verify_signature': True,
                'verify_exp': True
            },
            audience=audience,
            issuer=issuer)
    except JWTError:
        payload = jwt.decode(
            authorization_token,
            public_key,
            algorithms=['RS256'],
            options={
                'verify_signature': True,
                'verify_exp': True
            })
    return payload


# authorization decorator
def token_required(f):
    """Authenticate that a valid Token is present."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # check that the Authorization header is set
        authorization_token = request.headers.get('Authorization')
        if not authorization_token:
            return response_builder(dict(
                                    message="Bad request. Header does"
                                    "not contain authorization token"), 400)

        unauthorized_message = "Unauthorized. The authorization token " \
                               "supplied is invalid"

        try:
            # decode token
            public_key = base64.b64decode(
                current_app.config['PUBLIC_KEY']).decode("utf-8")
            payload = verify_token(authorization_token,
                                   public_key,
                                   current_app.config['API_AUDIENCE'],
                                   current_app.config['API_ISSUER'])
        except ExpiredSignatureError:
            expired_response = "The authorization token supplied is expired"
            return response_builder(dict(message=expired_response), 401)
        except JWTError:
            return response_builder(dict(message=unauthorized_message), 401)

        expected_user_info_format = {
            "id": "user_id",
            "email": "gmail",
            "first_name": "test",
            "last_name": "user",
            "name": "test user",
            "picture": "link",
            "roles": {
                "Andelan": "unique_id",
                "Fellow": "unique_id"
            }
        }
        expected_user_keys = expected_user_info_format.keys()
        payload_user_keys = payload.get("UserInfo").keys()

        # confirm that payload and UserInfo has required keys
        if ("UserInfo" and "exp") not in payload.keys():
            return response_builder(dict(message=unauthorized_message), 401)
        elif not all(item in payload_user_keys for item in expected_user_keys):
            return response_builder(dict(message=unauthorized_message), 401)
        else:
            user = User.query.get(payload["UserInfo"]["id"])
            if not user:
                user = store_user_details(payload, authorization_token)
            g.current_user = user
            g.current_user_token = authorization_token

            # attempt to link user to society
            if not g.current_user.society and g.current_user.cohort:
                user.society = g.current_user.cohort.society
                user.save()
        return f(*args, **kwargs)
    return decorated


def roles_required(roles):
    """Ensure only authorised roles may access sensitive data.

    params:
        roles (list): [str]
    """
    def check_user_role(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            route_roles = list(filter(lambda r: r is not None,
                                      [Role.query.filter_by(name=role).first()
                                       for role in roles]))
            for role in g.current_user.roles:
                if role in route_roles:
                    break
            else:
                return response_builder(
                    dict(message="You're unauthorized"
                         " to perform this operation"), 401)
            return f(*args, **kwargs)
        return decorated
    return check_user_role

