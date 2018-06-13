"""Society Module."""

from flask import request, g
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.utils.helpers import find_item, paginate_items, response_builder
from api.utils.marshmallow_schemas import (cohort_schema, base_schema,
                                            society_schema,
                                            user_logged_activities_schema)
from ..models import Society, Cohort, RedemptionRequest, LoggedActivity


class SocietyResource(Resource):
    """To contain CRUD endpoints for Society."""

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def post(cls):
        """Create a society."""
        payload = request.get_json(silent=True)
        if payload:
            try:
                name = payload["name"]
                color_scheme = payload["colorScheme"]
                logo = payload["logo"]
                photo = payload["photo"]
            except KeyError:
                return response_builder(dict(
                    status="fail",
                    message="Name, color scheme and logo are required"
                            " to create a society."
                    ), 400)

            # if no errors occur in assigning above
            society = Society(
                name=name, color_scheme=color_scheme, logo=logo, photo=photo
            )
            society.save()
            return response_builder(dict(
                status="success",
                data=society.serialize(),
                message="Society created successfully."
            ), 201)

        return response_builder(dict(
            status="fail",
            message="Data for creation must be provided"), 400)

    @classmethod
    @token_required
    def get(cls, society_id=None):
        """Get Society(ies) details."""
        if society_id:
            society = Society.query.get(society_id)
        elif request.args.get('name'):
            society = Society.query.filter_by(
                name=request.args.get('name')).first()
        else:
            # if no search term has been passed, return all societies in DB
            societies = Society.query
            return paginate_items(societies)

        if society:
            society_logged_activities = LoggedActivity.query.filter_by(
                society_id=society.uuid).all()

            data, _ = society_schema.dump(society)
            data['loggedActivities'], _ = user_logged_activities_schema.dump(
                society_logged_activities)

            return response_builder(dict(
                societyDetails=data,
                message="{} fetched successfully.".format(society.name)
            ), 200)
        else:
            return response_builder(dict(
                data=None,
                message="Resource does not exist."
            ), 404)

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls, society_id=None):
        """Edit Society details."""
        payload = request.get_json(silent=True)
        if payload:
            if not society_id:
                return response_builder(dict(
                    status="fail",
                    message="Society to be edited must be provided"), 400)

            society = Society.query.get(society_id)
            if society:
                try:
                    name = payload["name"] or None
                    color_scheme = payload["colorScheme"] or None
                    logo = payload["logo"] or None
                    photo = payload["photo"]or None
                    if name:
                        society.name = name
                    if color_scheme:
                        society.color = color_scheme
                    if photo:
                        society.photo = logo
                    if logo:
                        society.logo = photo
                    society.save()
                    return response_builder(dict(
                        data=society.serialize(),
                        status="success",
                        message="Society edited successfully."
                    ), 200)

                except KeyError as e:
                    return response_builder(dict(
                        module="Society Module",
                        errors=e), 500)

            return response_builder(dict(
                                status="fail",
                                message="Society does not exist."), 404)

        # if payload does not exist
        return response_builder(dict(
            status="fail",
            message="Data for editing must be provided"), 400)

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def delete(cls, society_id=None):
        """Delete Society."""
        if not society_id:
            return response_builder(dict(
                status="fail",
                message="Society id must be provided."), 400)

        society = Society.query.get(society_id)
        if not society:
            return response_builder(dict(
                status="fail",
                message="Society does not exist."), 404)

        society.delete()
        return response_builder(dict(
                status="success",
                message="Society deleted successfully."), 200)


class AddCohort(Resource):
    """Resource for adding cohorts to societies."""

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls):
        """Assign a cohort to a society.

        Returns
            response (dict): key:status
        """
        payload = request.get_json(silent=True)

        if not payload or not ('societyId' in payload and
                               'cohortId' in payload):
            return response_builder(dict(
                message="Error societyId and cohortId are required."
            ), 400)

        society = Society.query.filter_by(
            uuid=payload.get('societyId')).first()
        if not society:
            return response_builder(dict(
                message="Error Invalid societyId."
            ), 400)

        cohort = Cohort.query.filter_by(uuid=payload.get('cohortId')).first()
        if not cohort:
            return response_builder(dict(
                message="Error Invalid cohortId."
            ), 400)

        if cohort.society_id == society.uuid:
            return response_builder(dict(
                message="Cohort already in society."
            ), 409)

        society.cohorts.append(cohort)
        society.save()
        cohort.save()

        cohort_data = cohort_schema.dump(cohort).data
        cohort_meta_data = {
                'society': base_schema.dump(society).data,
                'country': base_schema.dump(cohort.country).data
                }
        cohort_data['meta'] = cohort_meta_data

        return response_builder(dict(
            message="Cohort added to society succesfully",
            data=cohort_data
        ), 200)


class PointRedemption(Resource):
    """
    Resource handling all point redemption requests.

    Only made by society presidents.
    """

    @classmethod
    @token_required
    @roles_required(["Society President"])
    def post(cls):
        """Create Redemption Request."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Redemption request must have data.",
                status="fail"
            ), 400)

        try:
            name = payload["name"],
            value = payload["value"]
        except KeyError:
            return response_builder(dict(
                message="Redemption request name and value required",
                status="fail"
            ), 400)

        redemp_request = RedemptionRequest(
            name=name,
            value=value,
            user=g.current_user
        )

        redemp_request.save()

        return response_builder(dict(
            message="Redemption request created. Success Ops will be in"
                    " touch soon.",
            status="success",
            data=redemp_request.serialize()
        ), 201)

    @classmethod
    @token_required
    @roles_required(["Society President", "Success Ops"])
    def put(cls, redeem_id=None):
        """Edit Redemption Requests."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="Redemption Request to be edited must be provided"),
                400)

        redemp_request = RedemptionRequest.query.filter_by(
                            uuid=redeem_id).first()
        if not redemp_request:
            return response_builder(dict(
                                status="fail",
                                message="RedemptionRequest does not exist."),
                                404)
        try:
            name = payload["name"]
            value = payload["value"]

            if name:
                redemp_request.name = name
            if value:
                redemp_request.color = value

            redemp_request.save()

            return response_builder(dict(
                data=redemp_request.serialize(),
                status="success",
                message="RedemptionRequest edited successfully."
            ), 200)

        except KeyError as e:
            return response_builder(dict(
                module="RedemptionRequest Module",
                errors=e), 500)

    @classmethod
    @token_required
    def get(cls, redeem_id=None):
        """Get Redemption Requests."""
        if not redeem_id:
            redemption_requests = RedemptionRequest.query
            return paginate_items(redemption_requests)

        if not redeem_id:
            search_term_name = request.args.get('name')
            if search_term_name:
                redemp_request = RedemptionRequest.query.filter_by(
                                        name=search_term_name).first()
                return find_item(redemp_request)

            search_term_status = request.args.get('status')
            if search_term_status:
                redemp_request = RedemptionRequest.query.filter_by(
                                        status=search_term_status)
                return paginate_items(redemp_request)

            search_term_society = request.args.get('society')
            if search_term_society:
                society = Society.query.filter_by(
                                name=search_term_society).first()

                redemp_request = RedemptionRequest.query.filter_by(
                                        redemp_request.user.society_id ==
                                        society.uuid
                                        ).first()
                return paginate_items(redemp_request)

        redemp_request = RedemptionRequest.query.get(redeem_id)
        return find_item(redemp_request)

    @classmethod
    @token_required
    @roles_required(["Success Ops", "Society President"])
    def delete(cls, redeem_id=None):
        """Delete Redemption Requests."""
        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest does not exist."), 404)

        redemp_request.delete()
        return response_builder(dict(
                status="success",
                message="RedemptionRequest deleted successfully."), 200)


class PointRedemptionRequestNumeration(Resource):
    """
    Approve or reject Redemption Requests.

    After approval or rejection the relevant society get the result of the
    request reflects on the amount of points.
    Only done by Success Ops.
    """

    @classmethod
    @token_required
    @roles_required(["Success Ops"])
    def put(cls, redeem_id=None):
        """Approve or Reject Redemption requests."""
        payload = request.get_json(silent=True)
        if not payload:
            return response_builder(dict(
                message="Data for editing must be provided",
                status="fail"
            ), 400)

        if not redeem_id:
            return response_builder(dict(
                status="fail",
                message="RedemptionRequest id must be provided."), 400)

        try:
            status = payload["status"]
        except KeyError as e:
            return response_builder(dict(
                module="RedemptionRequest Module",
                errors=e,
                message="Missing fields"), 400)

        redemp_request = RedemptionRequest.query.get(redeem_id)
        if not redemp_request:
            return response_builder(dict(
                data=None,
                status="fail",
                message="Resource does not exist."
            ), 404)

        if status == "approved":
            user = redemp_request.user
            society = Society.query.get(user.society_id)
            society.used_points = redemp_request
            redemp_request.status = status
        else:
            redemp_request.status = status

        return response_builder(dict(
            message="RedemptionRequest status changed to {}".format(
                                                        redemp_request.status),
            status="success",
            data=redemp_request.serialize()
        ), 200)
