"""Module test user information reource."""
import json
from unittest import mock

from flask import Response

from tests.base_test import BaseTestCase, Center, Cohort, Society
from api.utils.marshmallow_schemas import basic_info_schema


def info_mock(status_code, society=None, location=None, cohort=None, data=None):
    """Mock reponses from api calls to ANDELA API."""
    data = {} if not data else data
    api_response = Response()
    api_response.json = lambda: data
    api_response.status_code = status_code
    return cohort, location, api_response


class UserInformationTestCase(BaseTestCase):
    """Test get user information reource."""

    def setUp(self):
        """Set up patch information for every test."""
        super().setUp()
        self.nairobi.save()
        self.cohort_12_Ke.save()
        self.society = Society(name="iStelle")
        self.society.cohorts.append(self.cohort_12_Ke)
        self.society.save()

        cohort = self.cohort_12_Ke
        self.patcher = mock.patch('api.utils.auth.add_extra_user_info',
                                  return_value=info_mock(200,
                                                         location=self.nairobi,
                                                         cohort=cohort,
                                                         society=self.society))
        self.patcher.start()

    def test_get_user_info_saved_in_DB(self):
        """Test retrive saved information sucesfully."""
        self.cohort_1_Nig.save()
        self.phoenix.cohorts.append(self.cohort_1_Nig)
        self.phoenix.save()
        self.test_user.save()

        response = self.client.get('/api/v1/users/-KdQsMt2U0ixIy_-yWTSZ',
                                   headers=self.header,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)

        expected_location_data, _ = basic_info_schema.dump(self.lagos)
        self.assertDictEqual(response_data.get('data').get('location'),
                             expected_location_data)
        expected_society_data, _ = basic_info_schema.dump(self.phoenix)
        self.assertDictEqual(response_data.get('data').get('society'),
                             expected_society_data)
        expected_cohort_data, _ = basic_info_schema.dump(self.cohort_1_Nig)
        self.assertDictEqual(response_data.get('data').get('cohort'),
                             expected_cohort_data)

    def test_get_user_info_not_saved_in_DB(self):
        """Test retrive user info from ANDELA API sucesfully."""
        mock_location = Center(name='Mock-location')
        mock_location.save()
        mock_cohort = Cohort(name="mock_cohort", center=mock_location)
        mock_cohort.save()
        mock_society = Society(name="Mock-society")
        mock_society.cohorts.append(mock_cohort)
        mock_society.save()

        # build mock reponse
        user_mock_response = {
            'email': "mock.user.societies@andela.com",
            'first_name': "mock_user",
            'id': "-Krwrwahorgt-mock-user-id",
            'last_name': "mock_user",
            'picture': "https://www.link.com/picture_id",
            'location': {'id': mock_location.uuid},
            'cohort': {'id': mock_cohort.uuid},
            'roles': {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-KXGy1EB1oimjQgFim6C"
            }
        }

        patcher = mock.patch('api.endpoints.users.add_extra_user_info',
                             return_value=info_mock(200,
                                                    society=mock_society,
                                                    location=mock_location,
                                                    cohort=mock_cohort,
                                                    data=user_mock_response))
        patcher.start()

        response = self.client.get('/api/v1/users/-Krwrwahorgt-mock-user-id',
                                   headers=self.header,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)

        expected_location_data, _ = basic_info_schema.dump(mock_location)
        self.assertDictEqual(response_data.get('data').get('location'),
                             expected_location_data)

        expected_society_data, _ = basic_info_schema.dump(mock_society)
        self.assertDictEqual(response_data.get('data').get('society'),
                             expected_society_data)

        expected_cohort_data, _ = basic_info_schema.dump(mock_cohort)
        self.assertDictEqual(response_data.get('data').get('cohort'),
                             expected_cohort_data)

        patcher.stop()

    @mock.patch('api.endpoints.users.add_extra_user_info',
                return_value=info_mock(404, data={"error": "user not found"}))
    def test_get_user_info_404(self, mocked_func):
        """Test handles user not found."""
        response = self.client.get('/api/v1/users/-KoJA5HXKK5nVeIdc2Sv',
                                   headers=self.header,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertDictEqual(response_data, {"error": "user not found"})

    @mock.patch('api.endpoints.users.add_extra_user_info',
                return_value=info_mock(503, data={"Error": "Network Error"}))
    def test_get_user_info_503(self, mocked_func):
        """Test handles failed network connection correctly."""
        response = self.client.get('/api/v1/users/-KoJA5HXKK5nVeIdc2Sv',
                                   headers=self.header,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 503)
        response_data = json.loads(response.data)
        self.assertDictEqual(response_data, {"Error": "Network Error"})

    @mock.patch('api.endpoints.users.add_extra_user_info',
                return_value=info_mock(500,
                                       data={"Error": "Something went wrong"}))
    def test_get_user_info_500(self, mocked_func):
        """Test handles unexpected API issues correctly."""
        response = self.client.get('/api/v1/users/-KoJA5HXKK5nVeIdc2Sv',
                                   headers=self.header,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertDictEqual(response_data, {"Error": "Something went wrong"})
