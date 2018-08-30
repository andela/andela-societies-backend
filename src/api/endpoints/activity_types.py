"""Module for activity types operations."""

from flask import request
from flask_restful import Resource

from api.models import ActivityType
from api.utils.auth import roles_required, token_required
from api.utils.helpers import find_item, response_builder
from api.utils.marshmallow_schemas import (activity_types_schema,
                                           new_activity_type_schema)


class ActivityTypesAPI(Resource):
    """Activity Categories Resource."""

    decorators = [token_required]

    @classmethod
    @roles_required(["success ops"])
    def post(cls):
        """Create new activity type."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                                    message="Data for creation must "
                                            "be provided.",
                                    status="fail",
                                    ), 400)

        result, errors = new_activity_type_schema.load(payload)

        if errors:
            status_code = new_activity_type_schema.context.get(
                'status_code')
            validation_status_code = status_code or 400
            return response_builder(errors, validation_status_code)

        support_multiple = result.get("supports_multiple_participants")
        activity_type = ActivityType(
            name=result["name"],
            description=result["description"],
            value=result["value"],
            supports_multiple_participants=support_multiple
        )
        activity_type.save()
        return response_builder(dict(
            status="success",
            data=activity_type.serialize(),
            message="Activity type created successfully."
        ), 201)

    @classmethod
    def get(cls, act_types_id=None):
        """Get information on activity types."""
        search_term = request.args.get('q')
        if not search_term:
            if not act_types_id:
                activity_types = ActivityType.query.all()

                activity_types_list = activity_types_schema.dump(
                    activity_types).data

                return response_builder(dict(data=activity_types_list), 200)

            activity_type = ActivityType.query.get(act_types_id)
            return find_item(activity_type)

        activity_type = ActivityType.query.filter(
            ActivityType.name.ilike(f'%{search_term}%')
        ).first()
        return find_item(activity_type)

    @classmethod
    @roles_required(["success ops"])
    def put(cls, act_types_id=None):
        """Edit information on an activity type."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                                    message="Data for editing must "
                                            "be provided.",
                                    status="fail",
                                    ), 400)

        if not act_types_id:
            return response_builder(dict(
                                    message="Activity type to be edited"
                                            " must be provided",
                                    status="fail",
                                    ), 400)

        target_activity_type = ActivityType.query.get(act_types_id)
        if not target_activity_type:
            return response_builder(dict(
                status="fail",
                message="Resource not found."
            ), 404)

        if payload.get("name"):
            target_activity_type.name = payload.get("name")
        if payload.get("description"):
            target_activity_type.description = payload.get("description")
        if payload.get("value"):
            target_activity_type.value = payload.get("value")
        if payload.get("supports_multiple_participants"):
            target_activity_type.supports_multiple_participants =\
                payload.get("supports_multiple_participants")
        return response_builder(dict(
            message="Edit successful",
            path=target_activity_type.serialize(),
            status="success",
        ), 200)

    @classmethod
    @roles_required(["success ops"])
    def delete(cls, act_types_id=None):
        """Delete an activity type."""
        if not act_types_id:
            return response_builder(dict(
                status="fail",
                message="Activity type must be provided."
            ), 400)

        activity_type = ActivityType.query.get(act_types_id)
        if not activity_type:
            return response_builder(dict(
                message="Resource not found.",
                status="fail"
            ), 404)

        activity_type.delete()
        return response_builder(dict(
            status="success",
            message="Activity type deleted successfully."
        ), 200)
