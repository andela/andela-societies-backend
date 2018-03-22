"""Test Suite for Authorisation."""
import time
import json
from tests.base_test import BaseTestCase


class AuthTestCase(BaseTestCase):
    """Test authentication functionality."""

    def test_invalid_token(self):
        """Test response message if token is invalid."""
        invalid_token = {"Authorization": "WQ!DFTTEwqsds$4"}
        response = self.client.get('api/v1/societies',
                                   headers=invalid_token)

        self.assertTrue(response.status_code == 401)

        error_message = "Unauthorized. The authorization token " \
                        "supplied is invalid"

        response_message = response.data.decode('utf-8')
        self.assertIn(error_message, response_message)

    def test_expired_token(self):
        """Test if token being used has expired."""
        expired_token = self.generate_token(self.expired_payload)
        time.sleep(2)

        response = self.client.get('api/v1/societies',
                                   headers={"Authorization": expired_token})

        self.assertTrue(response.status_code == 401)

        error_message = "The authorization token supplied is expired"

        response_message = response.data.decode('utf-8')
        self.assertIn(error_message, response_message)

    def test_token_payload(self):
        """Test if the payload keys are valid."""
        token = self.generate_token(self.incomplete_payload)

        response = self.client.get('api/v1/societies',
                                   headers={"Authorization": token})

        self.assertTrue(response.status_code == 401)

        error_message = "Unauthorized. The authorization token " \
                        "supplied is invalid"

        response_message = response.data.decode('utf-8')
        self.assertIn(error_message, response_message)

    def test_unauthorised_role(self):
        """Test if unauthorised role can access endpoint."""
        unauthorised_token = self.generate_token(self.test_auth_role_payload)
        new_activity = dict(name="tech congress",
                            description="all about tech"
                            )

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=
                                    {"Authorization": unauthorised_token},
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertEqual(response.status_code, 401)

        message = "You're unauthorized to perform this operation"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
