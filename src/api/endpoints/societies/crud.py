from flask_restful import Resource
from flask import request

from api.utils.auth import token_required, roles_required
from api.endpoints.logged_activities.marshmallow_schemas import \
    user_logged_activities_schema
from api.utils.helpers import response_builder, paginate_items
from .models import Society
from .marshmallow_schemas import society_schema


class SocietyResource(Resource):
    """To contain CRUD endpoints for Society."""

    @classmethod
    @token_required
    @roles_required(["success ops"])
    def post(cls):
        """Create a society."""
        payload = request.get_json(silent=True)
        if payload:
            try:
                name = payload["name"]
                color_scheme = payload["colorScheme"]
                logo = payload["logo"]
                photo = payload["photo"]
            except KeyError:
                return response_builder(dict(
                    status="fail",
                    message="Name, color scheme and logo are required"
                            " to create a society."
                ), 400)

            # if no errors occur in assigning above
            society = Society(
                name=name, color_scheme=color_scheme, logo=logo, photo=photo
            )
            society.save()
            return response_builder(dict(
                status="success",
                data=society.serialize(),
                message="Society created successfully."
            ), 201)

        return response_builder(dict(
            status="fail",
            message="Data for creation must be provided"), 400)

    @classmethod
    @token_required
    def get(cls, society_id=None):
        """Get Society(ies) details."""
        if society_id:
            society = Society.query.get(society_id)
        elif request.args.get('name'):
            society = Society.query.filter_by(
                name=request.args.get('name')).first()
        else:
            # if no search term has been passed, return all societies in DB
            societies = Society.query
            return paginate_items(societies)

        if society:
            society_logged_activities = society.logged_activities.all()

            data, _ = society_schema.dump(society)
            data['loggedActivities'], _ = user_logged_activities_schema.dump(
                society_logged_activities)

            return response_builder(dict(
                societyDetails=data,
                message="{} fetched successfully.".format(society.name)
            ), 200)
        else:
            return response_builder(dict(
                data=None,
                message="Resource does not exist."
            ), 404)

    @classmethod
    @token_required
    @roles_required(["success ops"])
    def put(cls, society_id=None):
        """Edit Society details."""
        payload = request.get_json(silent=True)
        if payload:
            if not society_id:
                return response_builder(dict(
                    status="fail",
                    message="Society to be edited must be provided"), 400)

            society = Society.query.get(society_id)
            if society:
                try:
                    name = payload["name"] or None
                    color_scheme = payload["colorScheme"] or None
                    logo = payload["logo"] or None
                    photo = payload["photo"]or None
                    if name:
                        society.name = name
                    if color_scheme:
                        society.color = color_scheme
                    if photo:
                        society.photo = logo
                    if logo:
                        society.logo = photo
                    society.save()
                    return response_builder(dict(
                        data=society.serialize(),
                        status="success",
                        message="Society edited successfully."
                    ), 200)

                except KeyError as e:
                    return response_builder(dict(
                        module="Society Module",
                        errors=e), 500)

            return response_builder(dict(
                status="fail",
                message="Society does not exist."), 404)

        # if payload does not exist
        return response_builder(dict(
            status="fail",
            message="Data for editing must be provided"), 400)

    @classmethod
    @token_required
    @roles_required(["success ops"])
    def delete(cls, society_id=None):
        """Delete Society."""
        if not society_id:
            return response_builder(dict(
                status="fail",
                message="Society id must be provided."), 400)

        society = Society.query.get(society_id)
        if not society:
            return response_builder(dict(
                status="fail",
                message="Society does not exist."), 404)

        society.delete()
        return response_builder(dict(
            status="success",
            message="Society deleted successfully."), 200)
