"""Module for Logged Activities in Andela."""

from flask import g, request
from flask_restful import Resource
from sqlalchemy import func

from api.models import LoggedActivity, User, db
from api.utils.auth import token_required, roles_required
from api.utils.helpers import (ParsedResult, parse_log_activity_fields,
                               response_builder, paginate_items)
from api.utils.marshmallow_schemas import (
    log_edit_activity_schema, single_logged_activity_schema,
    logged_activities_schema, user_logged_activities_schema
)


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
            func.sum(LoggedActivity.value)
        ).filter(
            LoggedActivity.user_id == user_id,
            LoggedActivity.status == 'approved'
        ).scalar()

        return response_builder(dict(
            data=user_logged_activities_schema.dump(
                user_logged_activities).data,
            society=user.society.name if user.society else None,
            societyId=user.society.uuid if user.society else None,
            activitiesLogged=len(user_logged_activities),
            pointsEarned=points_earned if points_earned else 0,
            message=message
        ), 200)


class LoggedActivitiesAPI(Resource):
    """Logged Activities Resources."""

    decorators = [token_required]

    @classmethod
    def post(cls):
        """Log a new activity."""
        payload = request.get_json(silent=True)

        if payload:
            result, errors = log_edit_activity_schema.load(payload)

            if errors:
                return response_builder(dict(validationErrors=errors), 400)

            society = g.current_user.society
            if not society:
                return response_builder(dict(
                    message='You are not a member of any society yet'
                ), 422)

            parsed_result = parse_log_activity_fields(result)
            if not isinstance(parsed_result, ParsedResult):
                return parsed_result

            # log activity
            logged_activity = LoggedActivity(
                name=result.get('name'),
                description=result.get('description'),
                society=society,
                user=g.current_user,
                activity=parsed_result.activity,
                photo=result.get('photo'),
                value=parsed_result.activity_value,
                no_of_participants=result.get('no_of_participants'),
                activity_type=parsed_result.activity_type,
                activity_date=parsed_result.activity_date
            )

            logged_activity.save()

            return response_builder(dict(
                data=single_logged_activity_schema.dump(logged_activity).data,
                message='Activity logged successfully'
            ), 201)

        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)

    @classmethod
    def get(cls):
        """Get all logged activities"""
        paginate = request.args.get("paginate", "true")
        message = "all Logged activities fetched successfully"

        if paginate.lower() == "false":
            logged_activities = LoggedActivity.query.all()
            count = LoggedActivity.query.count()
            data = {"count": count}
        else:
            logged_activities = LoggedActivity.query
            pagination_result = paginate_items(logged_activities,
                                               serialize=False)
            logged_activities = pagination_result.data
            data = {
                "count": pagination_result.count,
                "page": pagination_result.page,
                "pages": pagination_result.pages,
                "previous_url": pagination_result.previous_url,
                "next_url": pagination_result.next_url
            }

        data.update(dict(
            loggedActivities=logged_activities_schema.dump(
                logged_activities
            ).data))

        return response_builder(dict(data=data, message=message,
                                     status="success"), 200)


class LoggedActivityAPI(Resource):
    """Single Logged Activity Resources."""

    decorators = [token_required]

    @classmethod
    def put(cls, logged_activity_id=None):
        """Log a new activity."""
        payload = request.get_json(silent=True)

        if payload:
            log_edit_activity_schema.context = {'edit': True}
            result, errors = log_edit_activity_schema.load(payload)
            log_edit_activity_schema.context = {}

            if errors:
                return response_builder(dict(validationErrors=errors), 400)

            logged_activity = LoggedActivity.query.filter_by(
                uuid=logged_activity_id,
                user_id=g.current_user.uuid).one_or_none()
            if not logged_activity:
                return response_builder(dict(
                    message='Logged activity does not exist'
                ), 404)
            if logged_activity.status != 'in review':
                return response_builder(dict(
                    message='Not allowed. Activity is already in pre-approval.'
                ), 401)
            if not result.get('activity_type_id'):
                result['activity_type_id'] = logged_activity.activity_type_id

            if not result.get('date'):
                result['date'] = logged_activity.activity_date
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

            logged_activity.save()

            return response_builder(dict(
                data=single_logged_activity_schema.dump(logged_activity).data,
                message='Activity edited successfully'
            ), 200)

        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)

    @classmethod
    def delete(cls, logged_activity_id=None):
        """Delete a logged activity."""
        logged_activity = LoggedActivity.query.filter_by(
            uuid=logged_activity_id,
            user_id=g.current_user.uuid).one_or_none()

        if not logged_activity:
            return response_builder(dict(
                message='Logged Activity does not exist!'
            ), 404)

        if logged_activity.status != 'in review':
            return response_builder(dict(
                message='You are not allowed to perform this operation'
            ), 403)

        logged_activity.delete()
        return response_builder(dict(), 204)


class SecretaryReviewLoggedAcivityApi(Resource):
    """Enable society secretary to verify logged activities."""

    decorators = [token_required]

    @classmethod
    @roles_required(['society secretary'])
    def put(cls, logged_activity_id):
        """Put method on logged Activity resource."""
        payload = request.get_json(silent=True)

        if 'status' not in payload:
            return response_builder(dict(message='status is required.'),
                                    400)

        logged_activity = LoggedActivity.query.filter_by(
            uuid=logged_activity_id).first()
        if not logged_activity:
            return response_builder(dict(message='Logged activity not found'),
                                    404)

        if not (payload.get('status') in ['pending', 'rejected']):
            return response_builder(dict(message='Invalid status value.'),
                                    400)
        logged_activity.status = payload.get('status')
        logged_activity.save()

        return response_builder(
            dict(data=single_logged_activity_schema.dump(logged_activity).data,
                 message="successfully changed status"),
            200)
