from api.utils.helpers import response_builder

from .models import Role


def edit_role(payload, search_term):
    """Find and edit the role."""
    role = Role.query.get(search_term)
    # if edit request == stored value
    if not role:
        return response_builder(dict(status="fail",
                                     message="Role does not exist."), 404)

    try:
        if payload["name"] == role.name:
            return response_builder(dict(
                data=dict(path=role.serialize()),
                message="No change specified."
            ), 200)

        else:
            old_role_name = role.name
            role.name = payload["name"]
            role.save()

            return response_builder(dict(
                data=dict(path=role.serialize()),
                message="Role {} has been changed"
                        " to {}.".format(old_role_name, role.name)
            ), 200)

    except KeyError:
        return response_builder(
            dict(status="fail",
                 message="Name to edit to must be provided."), 400)
