from flask import request
from flask_restful import Resource

from api.services.auth import roles_required, token_required
from api.utils.helpers import response_builder


class SocietyRoleAPI(Resource):
    """Contains functionality to change Society Executives."""

    def __init__(self, **kwargs):
        """Inject dependacy for resource."""
        self.Role = kwargs['Role']
        self.Society = kwargs['Society']
        self.User = kwargs['User']

    @token_required
    @roles_required(["success ops"])
    def put(self):
        """Change the a society executives."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Executive for change must be provided"
            ), 400)

        if not (payload.get("role") and payload.get("society") and payload.get(
                "name")):
            return response_builder(dict(
                message="Role, society and individual for change "
                        "must be provided"
            ), 400)

        society = self.Society.query.filter_by(
            name=payload.get("society")).first()
        role_change = self.Role.query.filter_by(
            name=payload.get("role")).first()

        if not role_change:
            return response_builder(dict(
                message="Create role to be appended.",
                status="fail"
            ), 404)
        if not society:
            return response_builder(dict(
                message="Society not found",
                status="fail"
            ), 404)

        query_user_role_changing = role_change.users.filter_by(
            society=society
        ).one_or_none()

        if query_user_role_changing and \
                query_user_role_changing.society_id == society.uuid:
            old_exec = query_user_role_changing
        else:
            old_exec = None

        new_exec = self.User.query.filter_by(
            name=payload.get("name"),
            society=society
        ).first()

        if not new_exec:
            return response_builder(dict(
                message="New Executive member not found or does not"
                        " belong to society.",
                status="fail"
            ), 404)

        # Remove the old role from the outgoing executive
        if not old_exec:
            return response_builder(dict(
                message="Previous Executive not found.",
                status="fail"
            ), 404)

        for role in old_exec.roles.all():
            if role.uuid == role_change.uuid:
                old_exec.roles.remove(role)

        new_exec.roles.append(role_change)
        new_exec.save()

        return response_builder(dict(
            data=new_exec.serialize(),
            message="{} has been appointed {} of {}".format(
                new_exec.name, payload.get("role"), society.name),
            status="success"
        ), 200)
