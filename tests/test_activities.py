"""Test of Activities Module."""
import json

from tests.base_test import BaseTestCase


class ActivitiesTestCase(BaseTestCase):
    """Test activities endpoints."""

    def setUp(self):
        """Save required roles."""
        BaseTestCase.setUp(self)
        self.successops_role.save()
        self.fellow_role.save()
        self.success_role.save()
        self.finance_role.save()

    def test_create_activity(self):
        """Test that an activity has been created successfully."""
        new_activity = dict(name="tech congress",
                            description="all about tech"
                            )

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.header,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertEqual(response.status_code, 201)

        message = "Activity created succesfully."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])

    def test_empty_request_object(self):
        """Test for empty request object."""
        new_activity = dict()

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.header,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertEqual(response.status_code, 400)

        message = "name and description required"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])

    def test_name_not_given(self):
        """Test for scenario where name not provided in request object."""
        new_activity = dict(description="all about tech")

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.header,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertTrue(response.status_code == 400)

        message = "Name is required to create an activity."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])

    def test_save_existing_activity(self):
        """Test attempt to save an already existing activity."""
        # store activity to the database
        self.js_meet_up.save()

        existing_activity = dict(
            name="Nairobi Js meetup",
            description="all about js"
        )

        # attempt to save the already existing activity
        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(existing_activity),
                                    headers=self.header,
                                    content_type='application/json')

        self.assertTrue(json.loads(response.data))
        self.assertTrue(response.status_code == 405)

        message = "Activity already exists!"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
