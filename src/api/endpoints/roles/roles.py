"""Module for Roles."""

from flask import request
from flask_restful import Resource

from api.services.auth import roles_required, token_required
from api.utils.helpers import find_item, paginate_items, response_builder

from .helpers import edit_role
from .marshmallow_schemas import role_schema


class RoleAPI(Resource):
    """Contain CRUD endpoints for Role."""

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.Role = kwargs['Role']

    @token_required
    @roles_required(["success ops"])
    def post(self):
        """Create a Role."""
        payload = request.get_json(silent=True)
        if payload:
            result, errors = role_schema.load(payload)

            if errors:
                status_code = role_schema.context.get('status_code')
                validation_status_code = status_code or 400
                return response_builder(errors, validation_status_code)

            role = self.Role(name=result['name'])
            role.save()
            return response_builder(dict(message='Role created successfully.',
                                         data=role.serialize()), 201)

        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)

    @token_required
    def get(self, role_query=None):
        """Get Role(s) from API."""
        if role_query:
            role = self.Role.query.get(role_query)
            return find_item(role)
        else:
            search_term = request.args.get('q')
            if search_term:
                role = self.Role.query.filter(self.Role.name.ilike(
                    f'%{search_term}%')).first()
                return find_item(role)
            else:
                roles = self.Role.query
                return paginate_items(roles)

    @classmethod
    @token_required
    @roles_required(["success ops"])
    def put(cls, role_query=None):
        """Edit a role's details."""
        payload = request.get_json(silent=True)

        if not payload:
            return response_builder(dict(
                                    message="Data for editing must "
                                            "be provided"),
                                    400)
        if not role_query:
            return response_builder(
                dict(
                    status="fail",
                    message="Role id/name must be provided."
                ),
                400
            )

        return edit_role(payload, role_query)

    @token_required
    @roles_required(["success ops"])
    def delete(self, role_query=None):
        """Delete a role."""
        if not role_query:
            return response_builder(
                dict(status="fail",
                     message="Role id must be provided."), 400)

        role = self.Role.query.get(role_query)
        if not role:
            return response_builder(
                dict(
                    status="fail",
                    message="Role does not exist."
                ),
                404)

        role.delete()
        return response_builder(
            dict(
                status="success",
                message="Role deleted successfully."
            ),
            200)
