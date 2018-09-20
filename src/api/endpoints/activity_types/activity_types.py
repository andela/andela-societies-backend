"""Module for activity types operations."""

from flask import request
from flask_restful import Resource

from api.services.auth import roles_required, token_required
from api.utils.helpers import find_item, response_builder

from .marshmallow_schemas import (activity_types_schema,
                                  new_activity_type_schema,
                                  edit_activity_type_schema)


class ActivityTypesAPI(Resource):
    """Activity Categories Resource."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependency for resource."""
        self.ActivityType = kwargs['ActivityType']

    @roles_required(["success ops"])
    def post(self):
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
        activity_type = self.ActivityType(
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

    def get(self, act_types_id=None):
        """Get information on activity types."""
        search_term = request.args.get('q')
        if not search_term:
            if not act_types_id:
                activity_types = self.ActivityType.query.all()

                activity_types_list = activity_types_schema.dump(
                    activity_types).data

                return response_builder(dict(data=activity_types_list), 200)

            activity_type = self.ActivityType.query.get(act_types_id)
            return find_item(activity_type)

        activity_type = self.ActivityType.query.filter(
            self.ActivityType.name.ilike(f'%{search_term}%')
        ).first()
        return find_item(activity_type)

    @roles_required(["success ops"])
    def put(self, act_types_id=None):
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

        target_activity_type = self.ActivityType.query.get(act_types_id)
        if not target_activity_type:
            return response_builder(dict(
                status="fail",
                message="Resource not found."
            ), 404)

        result, errors = edit_activity_type_schema.load(payload, partial=True)

        new_data = [
            (key, result[key]) for key in result
            if getattr(target_activity_type, key) != result[key]
        ]

        if errors:
            status_code = edit_activity_type_schema.context.get(
                'status_code')
            validation_status_code = status_code or 400
            return response_builder(errors, validation_status_code)

        for data in new_data: setattr(target_activity_type, *data)

        # save the model here
        target_activity_type.save()

        return response_builder(dict(
            message="Edit successful",
            data=target_activity_type.serialize(),
            status="success",
        ), 200)

    @roles_required(["success ops"])
    def delete(self, act_types_id=None):
        """Delete an activity type."""
        if not act_types_id:
            return response_builder(dict(
                status="fail",
                message="Activity type must be provided."
            ), 400)

        activity_type = self.ActivityType.query.get(act_types_id)
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
