"""Module for Users in platform."""
from flask import g
from flask_restful import Resource

from api.services.auth import token_required, add_extra_user_info
from api.utils.marshmallow_schemas import basic_info_schema

from .marshmallow_schema import user_schema


class UserAPI(Resource):
    """User Resource."""

    def __init__(self, **kwargs):
        """Inject dependacy for resource."""
        self.User = kwargs['User']
        self.Center = kwargs['Center']
        self.Cohort = kwargs['Cohort']

    @token_required
    def get(self, user_id=None):
        """Get user information."""
        user_information = {}
        status_code = None
        user = self.User.query.filter_by(uuid=user_id).first()

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
                'centerId': None,
                'cohortId': None,
                'roles': []
            }

            data['id'] = user_info.json().get('id')
            data['email'] = user_info.json().get('email')
            data['name'] = (f"{user_info.json().get('first_name')} "
                            f"{user_info.json().get('last_name')}")
            data['photo'] = user_info.json().get('picture')
            data['centerId'] = user_info.json().get('location').get('id')
            data['cohortId'] = user_info.json().get('cohort').get('id')
            user_information = data
            status_code = user_info.status_code

        location, _ = basic_info_schema.dump(
            self.Center.query.filter_by(
                uuid=user_information.pop('centerId')).first())
        user_information['location'] = location

        cohort = self.Cohort.query.filter_by(
            uuid=user_information.pop('cohortId')).first()
        if cohort:
            cohort_serialized, _ = basic_info_schema.dump(cohort)
            user_information['cohort'] = cohort_serialized
            user_information['society'], _ = basic_info_schema.dump(
                cohort.society)

        user_information['roles'] = {role['name']: role['id']
                                     for role in user_information['roles']}

        return dict(data=user_information), status_code
