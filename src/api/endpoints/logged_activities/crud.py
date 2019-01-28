from flask_restful import Resource
from flask import g, request

from api.services.auth import token_required
from api.utils.helpers import response_builder, paginate_items

from .helpers import ParsedResult, parse_log_activity_fields
from .marshmallow_schemas import (
    LogEditActivitySchema, single_logged_activity_schema,
    logged_activities_schema
)
from api.models import Role, User, Society

class LoggedActivitiesAPI(Resource):
    """Logged Activities Resources."""

    decorators = [token_required]

    def __init__(self, **kwargs):
        """Inject dependencies for resource."""
        self.Activity = kwargs['Activity']
        self.ActivityType = kwargs['ActivityType']
        self.LoggedActivity = kwargs['LoggedActivity']

    def post(self):
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
                result,
                self.Activity,
                self.ActivityType
            )
            if not isinstance(parsed_result, ParsedResult):
                return parsed_result

            # log activity
            logged_activity = self.LoggedActivity(
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
            # query = User.db.session.query(User).join(Role, Role.name == 'society secretary')
            # print(query.all())

            # logged_activity.save()
            
            society_id = g.current_user.society_id
            # roles = Role.query.filter_by(Role.users.user_role.any(name="secretary")).all()
            # roles = Role.query.join(User).order_by(UserRole.name)
            # society_query = Society.query.all()
            query = User.query.join(Role)
            roles = query.order_by(User.roles).all()

            # query = User.query(User).join(User.roles).join(Role.name)
            print(roles)


            return response_builder(dict(
                data=single_logged_activity_schema.dump(logged_activity).data,
                message='Activity logged successfully'
            ), 201)

        return response_builder(dict(
                                message="Data for creation must be provided."),
                                400)

    def get(self):
        """Get all logged activities."""
        paginate = request.args.get("paginate", "true")
        message = "all Logged activities fetched successfully"

        if paginate.lower() == "false":
            logged_activities = self.LoggedActivity.query.all()
            count = self.LoggedActivity.query.count()
            data = {"count": count}
        else:
            logged_activities = self.LoggedActivity.query
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

    def put(self, logged_activity_id=None):
        """Edit an activity."""
        payload = request.get_json(silent=True)

        if payload:
            log_edit_activity_schema = LogEditActivitySchema()
            log_edit_activity_schema.context = {'edit': True}
            result, errors = log_edit_activity_schema.load(payload)

            if errors:
                return response_builder(dict(validationErrors=errors), 400)

            logged_activity = self.LoggedActivity.query.filter_by(
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
            parsed_result = parse_log_activity_fields(
                result,
                self.Activity,
                self.ActivityType
            )
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

    def delete(self, logged_activity_id=None):
        """Delete a logged activity."""
        logged_activity = self.LoggedActivity.query.filter_by(
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
