"""
Authorisation Module.

This module contains the authorisation required by the client to
communicate with the API.
"""
import base64
from functools import wraps

from flask import current_app, g, request
from jose import ExpiredSignatureError, JWTError, jwt

from .helpers import store_user_details
from api.models import Role, User
from api.utils.helpers import response_builder


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

        # confirm that payload and UserInfo has required keys
        if ("UserInfo" and "exp") not in payload.keys():
            return response_builder(dict(message=unauthorized_message), 401)
        elif not payload["UserInfo"].get("id"):
            return response_builder(dict(message="malformed token"), 401)
        else:
            user = User.query.get(payload["UserInfo"]["id"])  #TODO check if user id exists
            # user id returns the name of the user
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
    """Ensure only authorized roles may access sensitive data.

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
