from flask_restful import Resource
from flask import request

from api.services.auth import token_required, roles_required
from api.utils.helpers import response_builder
from api.utils.marshmallow_schemas import basic_info_schema

from .marshmallow_schemas import cohort_schema


class Cohorts(Resource):
    """Resource for cohorts crud operations."""

    def __init__(self, **kwargs):
        """Inject dependacy for resource."""
        self.Cohort = kwargs['Cohort']
        self.Society = kwargs['Society']

    @token_required
    @roles_required(["success ops"])
    def put(self):
        """Assign a cohort to a society.

        Return
            response (dict): key:status

        """
        payload = request.get_json(silent=True)

        if not payload or not ('societyId' in payload and
                               'cohortId' in payload):
            return response_builder(dict(
                message="Error societyId and cohortId are required."
            ), 400)

        society = self.Society.query.filter_by(
            uuid=payload.get('societyId')).first()
        if not society:
            return response_builder(dict(
                message="Error Invalid societyId."
            ), 400)

        cohort = self.Cohort.query.filter_by(uuid=payload.get(
            'cohortId')).first()
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

        cohort_data = cohort_schema.dump(cohort).data
        cohort_meta_data = {
            'society': basic_info_schema.dump(society).data,
            'center': basic_info_schema.dump(cohort.center).data
        }
        cohort_data['meta'] = cohort_meta_data

        return response_builder(dict(
            message="Cohort added to society successfully",
            data=cohort_data
        ), 200)
