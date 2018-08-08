"""Authorization Test Suite."""
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
