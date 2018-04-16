"""Module for Activities in Andela."""
from flask import jsonify, request
from flask_restplus import Resource

from api.utils.auth import (token_required, roles_required)
from api.models import Activity


class ActivitiesAPI(Resource):
    """Activity Resource to contain CRUD endpoints for activities."""

    @token_required
    @roles_required(["Success Ops"])
    def post(self):
        """Create an activity."""
        payload = request.get_json()

        if not payload:
            response = jsonify({
                "status": "fail",
                "message": "name and description required"})
            response.status_code = 400
        elif "name" not in payload.keys():
            response = jsonify({
                    "status": "fail",
                    "message": "Name is required to create an activity."
                })
            response.status_code = 400

        else:
            name = payload["name"]
            description = payload["description"]

            existing_activity = Activity.query.filter(
                                Activity.name.ilike(name)).first()

            if existing_activity:
                response = jsonify({
                    "message": "Activity already exists!"
                })
                response.status_code = 405

            else:
                activity = Activity(
                    name=name, description=description)
                activity.save()

                response = jsonify({
                    "status": "success",
                    "data": activity.serialize(),
                    "message": "Activity created successfully."
                })
                response.status_code = 201

        return response
