"""Module for Roles."""

from flask import request
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from ..models import Role
from api.utils.helpers import (paginate_items, edit_role, find_item,
                               response_builder)
from api.utils.marshmallow_schemas import role_schema


class RoleAPI(Resource):
    """Contain CRUD endpoints for Role."""

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def post(cls):
        """Create a Role."""
        payload = request.get_json(silent=True)
        if payload:
            result, errors = role_schema.load(payload)

            if errors:
                status_code = role_schema.context.get('status_code')
                role_schema.context = {'Roles': Role.query.all()}
                validation_status_code = status_code or 400
                return response_builder(errors, validation_status_code)

            role = Role(name=result['name'])
            role.save()
            return response_builder(dict(message='Role created successfully.',
                                         data=result), 201)

        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)

    @classmethod
    @token_required
    def get(cls, role_query=None):
        """Get Role(s) from API."""
        if role_query:
            role = Role.query.get(role_query)
            return find_item(role)
        else:
            search_term = request.args.get('q')
            if search_term:
                role = Role.query.filter_by(name=search_term).first()
                return find_item(role)
            else:
                roles = Role.query
                return paginate_items(roles)

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls, role_query=None):
        """Edit a role's details."""
        payload = request.get_json(silent=True)

        if payload:
            if not role_query:
                return {"status": "fail",
                        "message": "Role id/name must be provided."}, 400

            return edit_role(payload, role_query)

        return response_builder(dict(
                                message="Data for editing must be provided"),
                                400)

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def delete(cls, role_query=None):
        """Delete a role."""
        if not role_query:
            return response_builder(
                        dict(status="fail",
                             message="Role id must be provided."), 400)

        role = Role.query.get(role_query)
        if not role:
            return response_builder(dict(status="fail",
                                    message="Role does not exist."), 404)

        role.delete()
        return response_builder(dict(status="success",
                                message="Role deleted successfully."), 200)
