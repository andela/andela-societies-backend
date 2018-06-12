"""Module for Users in platform."""
from flask_restplus import Resource
from flask import g
from api.utils.helpers import add_extra_user_info

from api.utils.auth import token_required
from api.utils.marshmallow_schemas import user_schema, basic_info_schema
from api.models import User, Cohort, Country


class UserAPI(Resource):
    """User Resource."""

    @classmethod
    @token_required
    def get(cls, user_id=None):
        """Get user information."""
        user_information = {}
        status_code = None
        user = User.query.filter_by(uuid=user_id).first()

        if user:
            user_information, _ = user_schema.dump(user)
            user_information['roles'], _ = basic_info_schema.dump(
                                            user.roles, many=True)
            status_code = 200
        else:
            _, _, user_info = add_extra_user_info(
                g.current_user_token, user_id)

            if user_info.status_code != 200:
                return user_info.json(), user_info.status_code

            data = {
                'createdAt': None,
                'description': None,
                'id': None,
                'name': None,
                'photo': None,
                'modifiedAt': None,
                'countryId': None,
                'cohortId': None,
                'roles': []
            }

            data['id'] = user_info.json().get('id')
            data['email'] = user_info.json().get('email')
            data['name'] = (f"{user_info.json().get('first_name')} "
                            f"{user_info.json().get('last_name')}")
            data['photo'] = user_info.json().get('picture')
            data['countryId'] = user_info.json().get('location').get('id')
            data['cohortId'] = user_info.json().get('cohort').get('id')
            user_information = data
            status_code = user_info.status_code

        location, _ = basic_info_schema.dump(
            Country.query.filter_by(
                uuid=user_information.pop('countryId')).first())
        cohort = Cohort.query.filter_by(
            uuid=user_information.pop('cohortId')).first()

        cohort_serialized, _ = basic_info_schema.dump(cohort)
        user_information['location'] = location
        user_information['cohort'] = cohort_serialized
        user_information['society'], _ = basic_info_schema.dump(cohort.society)

        return dict(data=user_information), status_code
