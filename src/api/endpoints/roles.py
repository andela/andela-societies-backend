"""Module for Roles."""

from flask import jsonify, request
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from ..models import Role
from api.utils.helpers import paginate_roles, edit_role, find_role
from api.utils.marshmallow_schemas import role_schema


class RoleAPI(Resource):
    """Contain CRUD endpoints for Role."""

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def post(cls):
        """Create a Role."""
        payload = request.get_json()

        result, errors = role_schema.load(payload)

        if errors:
            response = jsonify(errors)
            status_code = role_schema.context.get('status_code')
            role_schema.context = {'Roles': Role.query.all()}
            response.status_code = status_code or 400
        else:
            role = Role(name=result['name'])
            role.save()

            response = jsonify({'message': 'Role created successfully.',
                                'data': result})
            response.status_code = 201

        return response

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def get(cls, role_query=None):
        """Get Role(s) from API."""
        if role_query:
            role = Role.query.get(role_query)
            return find_role(role)
        else:
            search_term = request.args.get('q')
            if search_term:
                role = Role.query.filter_by(name=search_term).first()
                return find_role(role)
            else:
                return paginate_roles()

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls, role_query=None):
        """Edit a role's details."""
        payload = request.get_json()

        if payload:
            if not role_query:
                return {"status": "fail",
                        "message": "Role id/name must be provided."}, 400

            return edit_role(payload, role_query)

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def delete(cls, role_query):
        """Delete a role."""
        if not role_query:
            return {"status": "fail",
                    "message": "Role id must be provided."}, 400
        role = Role.query.get(role_query)
        if not role:
            response = jsonify({"status": "fail",
                                "message": "Role does not exist."})
            response.status_code = 404
            return response
        else:
            role.delete()
            response = jsonify({"status": "success",
                                "message": "Role deleted successfully."})
            response.status_code = 200
            return response
