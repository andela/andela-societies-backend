"""Module for Users in platform."""
from flask import g
from flask_restplus import Resource

from api.utils.auth import token_required
from api.utils.helpers import response_builder


class UserAPI(Resource):
    """User Resource."""

    @token_required
    def get(self):
        """Get user information."""
        try:
            _user = g.current_user
            user = _user.serialize()

            if _user.society:
                user["society"] = _user.society.name
            else:
                user["society"] = None

            logged_activities = []
            user_points = _user.logged_activities
            for _point in user_points:
                _activity = _point.activity
                activity = _activity.serialize()
                activity['status'] = _point.status
                activity['createdAt'] = _point.created_at
                activity['pointName'] = _point.name
                activity['pointDescription'] = _point.description
                activity['value'] = _point.value
                activity['timesLogged'] = len(user_points.filter_by(
                    activity_id=_activity.uuid).all())
                logged_activities.append(activity)

            user["loggedActivities"] = logged_activities
            logged_points = sum([point.value
                                for point in _user.logged_activities])
            user["totaLoggedPoints"] = logged_points

            return response_builder(dict(data=user,
                                    message='Profile retrieved successfully.'),
                                    200)

        except Exception as e:
            return response_builder(dict(
                                    errors=e,
                                    message="An error occured and the server"
                                            "was unable to complete the"
                                            "request."), 500)
