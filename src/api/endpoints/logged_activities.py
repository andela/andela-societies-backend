"""Module for Logged Activities in Andela."""
from flask import jsonify, request, g
from flask_restplus import Resource
from sqlalchemy import func

from api.models import LoggedActivity, User, db
from api.utils.auth import token_required
from api.utils.marshmallow_schemas import (
    user_logged_activities_schema, single_logged_activity_schema,
    log_edit_activity_schema
)
from api.utils.helpers import parse_log_activity_fields, ParsedResult


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
            societyId=user.society.uuid if user.society else None,
            activitiesLogged=len(user_logged_activities),
            pointsEarned=points_earned if points_earned else 0,
            message=message
        )


class LoggedActivitiesAPI(Resource):
    """Logged Activities Resources."""
    decorators = [token_required]

    def post(self):
        """Log a new activity"""
        payload = request.get_json()
        result, errors = log_edit_activity_schema.load(payload)

        if errors:
            return dict(validationErrors=errors), 400

        society = g.current_user.society
        if not society:
            return dict(
                message = 'You are not a member of any society yet'
            ), 422

        parsed_result = parse_log_activity_fields(result)
        if not isinstance(parsed_result, ParsedResult):
            return parsed_result

        # log activity
        logged_activity = LoggedActivity(
            name=result.get('name'), description=result.get('description'),
            society=society, user=g.current_user,
            activity=parsed_result.activity,
            photo=result.get('photo'), value=parsed_result.activity_value,
            activity_type=parsed_result.activity_type,
            activity_date=parsed_result.activity_date
        )

        db.session.add(logged_activity)
        db.session.commit()

        return dict(
            data=single_logged_activity_schema.dump(logged_activity).data,
            message='Activity logged successfully'
        ), 201


class LoggedActivityAPI(Resource):
    """Single Logged Activity Resources."""
    decorators = [token_required]

    def put(self, logged_activity_id):
        """Log a new activity"""
        payload = request.get_json()
        result, errors = log_edit_activity_schema.load(payload)

        if errors:
            return dict(validationErrors=errors), 400

        logged_activity = LoggedActivity.query.filter_by(
            uuid=logged_activity_id, user_id=g.current_user.uuid).one_or_none()
        if not logged_activity:
            return dict(
                message = 'Logged activity does not exist'
            ), 404
        if logged_activity.status != 'in review':
            return dict(
                message = 'Not allowed. Activity is already in pre-approval.'
            ), 401

        parsed_result = parse_log_activity_fields(result)
        if not isinstance(parsed_result, ParsedResult):
            return parsed_result

        # update fields
        logged_activity.name = result.get('name')
        logged_activity.description = result.get('description')
        logged_activity.activity = parsed_result.activity
        logged_activity.photo = result.get('photo')
        logged_activity.value = parsed_result.activity_value
        logged_activity.activity_type = parsed_result.activity_type
        logged_activity.activity_date = parsed_result.activity_date

        db.session.commit()

        return dict(
            data=single_logged_activity_schema.dump(logged_activity).data,
            message = 'Activity edited successfully'
        ), 200
