from flask_restful import Resource

from api.models import User
from api.utils.auth import token_required
from api.utils.helpers import response_builder
from .models import db, LoggedActivity
from .marshmallow_schemas import user_logged_activities_schema


class UserLoggedActivitiesAPI(Resource):
    """User Logged Activities Resources."""

    decorators = [token_required]

    @classmethod
    def get(cls, user_id):
        """Get a user's logged activities by user_id URL parameter."""
        user = User.query.get(user_id)
        if not user:
            return response_builder(dict(message="User not found"), 404)

        message = "Logged activities fetched successfully"
        user_logged_activities = user.logged_activities.all()

        if not user_logged_activities:
            message = "There are no logged activities for that user."

        points_earned = db.session.query(
            db.func.sum(LoggedActivity.value)
        ).filter(
            LoggedActivity.user_id == user_id,
            LoggedActivity.status == 'approved'
        ).scalar()

        return response_builder(dict(
            data=user_logged_activities_schema.dump(
                user_logged_activities
            ).data,
            society=user.society.name if user.society else None,
            societyId=user.society.uuid if user.society else None,
            activitiesLogged=len(user_logged_activities),
            pointsEarned=points_earned if points_earned else 0,
            message=message
        ), 200)
