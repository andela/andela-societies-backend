"""Test Suite for User endpoint."""

import json
from tests.base_test import BaseTestCase


class UserTestCase(BaseTestCase):
    """Test users endpoints."""

    def setUp(self):
        """Set up all needed variables."""
        BaseTestCase.setUp(self)
        self.kenya.save()
        self.cohort_12_Ke.save()
        self.phoenix.save()
        self.nigeria.save()
        self.cohort_1_Nig.save()
        self.test_user.save()
        self.alibaba_ai_challenge.save()
        self.log_alibaba_challenge.save()

    def test_get_user_information(self):
        """Test getting current user information."""
        response = self.client.get('api/v1/user/profile',
                                   headers=self.header,
                                   content_type='application/json')

        message = "Profile retrieved successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)
