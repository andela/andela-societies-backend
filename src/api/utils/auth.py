"""
Authorisation Module.

This module contains the authorisation required by the client to
communicate with the API.
"""
import base64
from functools import wraps
from flask import g, jsonify, request, current_app
from jose import ExpiredSignatureError, JWTError, jwt

from api.models import User, Role
from api.utils.helpers import add_extra_user_info, response_builder


def auth_response(status_code, message):
    """Build authentication responses."""
    response = jsonify({
        "message": message
    })
    response.status_code = status_code
    return response


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

            payload = jwt.decode(authorization_token,
                                 public_key,
                                 algorithms=['RS256'],
                                 options={
                                     'verify_signature': True,
                                     'verify_exp': True
                                 }
                                 )

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

        # confirm that payload and UserInfo has required keys
        if ("UserInfo" and "exp") not in payload.keys():
            return response_builder(dict(message=unauthorized_message), 401)
        elif payload["UserInfo"].keys() != expected_user_info_format.keys():
            return response_builder(dict(message=unauthorized_message), 401)
        else:
            store_user_details(payload, authorization_token)

            # now return wrapped function
            return f(*args, **kwargs)
    return decorated


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
        Role.query.filter_by(name=role).first() for role in roles
        if role != "Andelan" and Role.query.filter_by(
            name=role).first() is not None]

    user.save()

    g.current_user = user
    g.current_user_token = token


def roles_required(roles):  # roles should be a list
    """Ensure only authorised roles may access sensitive data."""
    def check_user_role(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not set(g.current_user.roles).issubset(
                    [Role.query.filter_by(name=role).first()
                     for role in roles]):
                return response_builder(dict(message="You're unauthorized"
                                             " to perform this operation"),
                                        401)
            return f(*args, **kwargs)
        return decorated
    return check_user_role
