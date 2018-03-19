import json

from api.models import User
from tests.base_test import BaseTestCase


class UserTestCase(BaseTestCase):
    """Test users endpoints."""

    def setUp(self):
        BaseTestCase.setUp(self)
        self.response = self.client.get('api/v1/user/profile', headers=self.header)

    def test_models(self):
        """ tests the user model data """
        self.assertEqual(self.response.status_code, 200)

        response_json = json.loads(self.response.get_data(as_text=True))
        user_id = response_json['data']['uuid']
        user_name = response_json['data']['name']
        user = User.query.get(user_id)

        self.assertEqual(user_name, user.name)

    def test_if_user_data_exists(self):
        """ test if user information is present in api response """
        mock_email = self.test_payload['UserInfo']['email']
        user_information = json.loads(self.response.data)


        self.assertEqual(mock_email, user_information['data']['email'])
