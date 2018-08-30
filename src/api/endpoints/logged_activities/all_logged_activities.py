from flask_restful import Resource
from flask import g, request

from api.models import Activity, ActivityType
from api.utils.auth import token_required
from api.utils.helpers import response_builder, paginate_items
from .models import LoggedActivity
from .helpers import ParsedResult, parse_log_activity_fields
from .marshmallow_schemas import (
    LogEditActivitySchema, single_logged_activity_schema,
    logged_activities_schema
)


class LoggedActivitiesAPI(Resource):
    """Logged Activities Resources."""

    decorators = [token_required]

    @classmethod
    def post(cls):
        """Log a new activity."""
        payload = request.get_json(silent=True)

        if payload:
            result, errors = LogEditActivitySchema().load(payload)

            if errors:
                return response_builder(dict(validationErrors=errors), 400)

            society = g.current_user.society
            if not society:
                return response_builder(dict(
                    message='You are not a member of any society yet'
                ), 422)

            parsed_result = parse_log_activity_fields(
                result, Activity, ActivityType
            )
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
                activity_type=parsed_result.activity_type,
                activity_date=parsed_result.activity_date
            )

            if logged_activity.activity_type.name == 'Bootcamp Interviews':
                if not result['no_of_participants']:
                    return response_builder(dict(
                                            message="Data for creation must be"
                                                    " provided. (no_of_"
                                                    "participants)"),
                                            400)
                else:
                    logged_activity.no_of_participants = result[
                        'no_of_participants'
                    ]

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
        """Get all logged activities."""
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
