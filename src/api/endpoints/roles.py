"""Module for Roles."""

from flask import request
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from ..models import Role, User, Society, user_role
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
                validation_status_code = status_code or 400
                return response_builder(errors, validation_status_code)

            role = Role(name=result['name'])
            role.save()
            return response_builder(dict(message='Role created successfully.',
                                         data=role.serialize()), 201)

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

        if not payload:
            return response_builder(dict(
                                    message="Data for editing must "
                                            "be provided"),
                                    400)
        if not role_query:
            return {"status": "fail",
                    "message": "Role id/name must be provided."}, 400

        return edit_role(payload, role_query)

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


class SocietyRoleAPI(Resource):
    """Contains functionality to change Society Executives."""

    @token_required
    @roles_required(["Success Ops"])
    def put(self):
        """Change the a society executives."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Executive for change must be provided"
            ), 400)

        if not payload.get("role") and payload.get("society") and payload.get(
                                                                    "name"):
            return response_builder(dict(
                message="Role, society and individual for change "
                        "must be provided"
            ), 400)

        society = Society.query.filter_by(name=payload.get("society")).first()
        role_change = Role.query.filter_by(name=payload.get("role")).first()

        query_user_role_changing = User.query.join(user_role).join(
                                   Role).filter(
                                   user_role.c.role_uuid
                                   == role_change.uuid).all()

        for user in query_user_role_changing:
            if user.society_id == society.uuid:
                old_exec = user
            else:
                old_exec = None

        new_exec = User.query.filter_by(name=payload.get("name")).first()

        # Remove the old role from the outgoing exceutive
        if not old_exec:
            return response_builder(dict(
                message="Previous Executive not found.",
                status="fail"
            ), 404)
        try:
            for role in old_exec.roles:
                if role.uuid == role_change.uuid:
                    old_exec.roles.remove(role)
        except ValueError:
            return response_builder(dict(
                message="Role not found in outgoing_exec",
                status="fail"
            ), 404)

        if not Role.query.filter_by(name="President").first():
            return response_builder(dict(
                message="Create role to be appended.",
                status="fail"
            ), 404)

        new_exec.roles.append(Role.query.filter_by(
                                    name=payload.get("role")).first())
        return response_builder(dict(
            data=new_exec.serialize(),
            message="{} has been appointed {} of {}".format(new_exec.name,
                                payload.get("role"), society.name),
            status="success"
        ), 200)
