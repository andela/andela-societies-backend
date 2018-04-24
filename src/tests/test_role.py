"""Test suite for restriction of endpoints by Role."""
import json

from .base_test import BaseTestCase


class RoleAPITestCase(BaseTestCase):
    """Holds tests for API concerning roles."""

    def setUp(self):
        """Save required roles."""
        BaseTestCase.setUp(self)
        self.successops_role.save()
        self.fellow_role.save()
        self.success_role.save()
        self.finance_role.save()

    def test_create_role(self):
        """Test Role creating succeeds."""
        new_role = dict(name="iStelle President")
        response = self.client.post('/api/v1/roles',
                                    data=json.dumps(new_role),
                                    headers=self.successops_role
                                    )

        self.assertTrue(json.loads(response.data))

        message = "Role created successfully."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 201)

    def test_create_role_without_name(self):
        """Test Role creation without name."""
        new_role = dict()
        response = self.client.post('/api/v1/roles',
                                    data=json.dumps(new_role),
                                    headers=self.successops_role
                                    )

        self.assertTrue(json.loads(response.data))

        message = "A name is required."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_name_role(self):
        """Test Role creating succeeds."""
        new_role = dict(name="Success Ops")
        response = self.client.post('/api/v1/roles',
                                    data=json.dumps(new_role),
                                    headers=self.successops_role
                                    )

        self.assertTrue(json.loads(response.data))

        message = "Role already exists!"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 409)


class RoleAuthTestCase(BaseTestCase):
    """Holds tests of roles in authentication."""

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

    def test_successops_can_create_activity(self):
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
