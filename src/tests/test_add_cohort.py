"""Test adding cohorts and getting cohorts from societies."""

import json
from tests.base_test import BaseTestCase, Role


class AddCohortTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.success_role = Role(name="success ops")
        self.success_role.save()

    def test_add_society(self):
        self.nairobi.save()
        self.istelle.save()
        self.cohort_12_Ke.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'cohortId': self.cohort_12_Ke.uuid,
                 'societyId': self.istelle.uuid}
            )
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        self.assertEqual("Cohort added to society succesfully", data['message'])
        self.assertEqual(
            data.get('data').get('meta').get('society')['id'],
            self.istelle.uuid
        )

    def test_add_society_reject_missing_cohort(self):
        self.istelle.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'societyId': self.istelle.uuid}
            )
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertDictEqual(data, dict(
            message="Error societyId and cohortId are required."))

    def test_add_society_reject_missing_society(self):
        self.cohort_12_Ke.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'cohortId': self.cohort_12_Ke.uuid}
            )
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertDictEqual(data, dict(
            message="Error societyId and cohortId are required."))

    def test_add_society_invalid_cohort(self):
        self.cohort_12_Ke.save()
        self.istelle.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'cohortId': "-K-3refaaaer:Invalid",
                 'societyId': self.istelle.uuid}
            )
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertDictEqual(data, dict(
            message="Error Invalid cohortId."))

    def test_add_society_invalid_society(self):
        self.cohort_12_Ke.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'cohortId': self.cohort_12_Ke.uuid,
                 'societyId': "-K-3refaaaer:Invalid"}
            )
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertDictEqual(data, dict(
            message="Error Invalid societyId."))

    def test_add_society_conflicting_data(self):
        self.nairobi.save()
        self.istelle.save()
        self.istelle.cohorts.append(self.cohort_12_Ke)
        self.cohort_12_Ke.save()
        self.istelle.save()

        response = self.client.put(
            '/api/v1/societies/cohorts',
            headers=self.success_ops, data=json.dumps(
                {'cohortId': self.cohort_12_Ke.uuid,
                 'societyId': self.istelle.uuid}
            )
        )

        self.assertEqual(response.status_code, 409)

        data = json.loads(response.data)
        self.assertDictEqual(data, dict(
            message="Cohort already in society."
            ))
