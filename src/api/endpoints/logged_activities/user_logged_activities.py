from flask_restful import Resource
from flask import g

from api.services.auth import token_required
from api.utils.helpers import response_builder, find_d_level

from .marshmallow_schemas import user_logged_activities_schema
from .models import db


class UserLoggedActivitiesAPI(Resource):
    """User Logged Activities Resources."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependencies for resource."""
        self.LoggedActivity = kwargs['LoggedActivity']
        self.User = kwargs['User']

    def get(self, user_id):
        """Get a user's logged activities by user_id URL parameter."""
        user = self.User.query.get(user_id)
        if not user:
            return response_builder(dict(message="User not found"), 404)

        message = "Logged activities fetched successfully"
        user_logged_activities = user.logged_activities.all()

        if not user_logged_activities:
            message = "There are no logged activities for that user."

        points_earned = db.session.query(
            db.func.sum(self.LoggedActivity.value)
        ).filter(
            self.LoggedActivity.user_id == user_id,
            self.LoggedActivity.status == 'approved'
        ).scalar()

        data=user_logged_activities_schema.dump(
                user_logged_activities
            ).data

        # Fetch D-level info
        user_level = find_d_level(g.current_user_token, user_id)
        return response_builder(dict(
            data=data,
            society=user.society.name if user.society else None,
            societyId=user.society.uuid if user.society else None,
            activitiesLogged=len(user_logged_activities),
            level=user_level,
            pointsEarned=points_earned if points_earned else 0,
            message=message
        ), 200)
