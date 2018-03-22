"""Test suite for restriction of endpoints by Role."""
import json

from .base_test import BaseTestCase


class RoleTestCase(BaseTestCase):
    """Holds tests of roles in authentication."""

    def test_fellow_cannot_create_activity(self):
        """Test if Fellow role can access Activity endpoint."""
        new_activity = dict(name="tech congress",
                            description="all about tech"
                            )

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.header,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertEqual(response.status_code, 401)

        message = "You're unauthorized to perform this operation"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])

    def test_successops__can_create_activity(self):
        """Test if Success Ops role can access Activity endpoint."""
        successops_token =\
            {"Authorization": self.generate_token(self.test_successops_payload)}
        new_activity = dict(name="tech congress",
                            description="all about tech"
                            )

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=successops_token,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertEqual(response.status_code, 401)

        message = "You're unauthorized to perform this operation"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
