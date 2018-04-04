"""Module for Logged Activities in Andela."""
from flask import jsonify
from flask_restplus import Resource
from sqlalchemy import func

from api.models import LoggedActivity, User, db
from api.utils.auth import token_required
from api.utils.marshmallow_schemas import user_logged_activities_schema


class UserLoggedActivitiesAPI(Resource):
    """Logged Activities Resources."""
    decorators = [token_required]

    def get(self, user_id):
        """Get a user's logged activities by user_id URL parameter"""
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        message = "Logged activities fetched successfully"
        user_logged_activities = user.logged_activities.all()

        if not user_logged_activities:
            message = "There are no logged activities for that user."

        points_earned = db.session.query(
            func.sum(LoggedActivity.value)
        ).filter(
                LoggedActivity.user_id == user_id,
                LoggedActivity.status == 'approved'
            ).scalar()

        return jsonify(
            data=user_logged_activities_schema.dump(
                user_logged_activities).data,
            society=user.society.name if user.society else None,
            society_id=user.society.uuid if user.society else None,
            activities_logged=len(user_logged_activities),
            points_earned=points_earned if points_earned else 0,
            message=message
        )
