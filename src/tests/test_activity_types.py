"""Activity Types Test Suite."""
import json

from api.models import ActivityType
from tests.base_test import BaseTestCase


class ActivityTypesTestCase(BaseTestCase):
    """Test activity types endpoints."""

    def setUp(self):
        """Set up all needed variables for the test."""
        BaseTestCase.setUp(self)
        self.successops_role.save()
        self.fellow_role.save()
        self.finance_role.save()
        self.lf_role.save()
        self.successops_token =\
            {"Authorization":
                self.generate_token(self.test_successops_payload)}
        self.hackathon.save()
        self.tech_event.save()

    def test_create_activity_type(self):
        """Test creation of new activity type is successful."""
        new_activity_type = dict(name="Blog Editor",
                                 description="Taking responsibilty for editing"
                                 " a blog for the Andela Way.",
                                 value=1000,
                                 supports_multiple_participants=False)

        response = self.client.post("/api/v1/activity-types",
                                    data=json.dumps(new_activity_type),
                                    headers=self.successops_token,
                                    content_type="application/json")

        message = "created successfully."
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 201)

    def test_create_existing_activity_type_name(self):
        """Test duplication of activity type is unsuccessful."""
        new_activity_type = dict(name="Hackathon",
                                 description="A Hackathon",
                                 value=1000,
                                 supports_multiple_participants=False)

        response = self.client.post("/api/v1/activity-types",
                                    data=json.dumps(new_activity_type),
                                    headers=self.successops_token,
                                    content_type="application/json")

        message = "already exists"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 409)

    def test_create_activity_type_no_payload(self):
        """Test creation of new activity type fails with no payload."""
        response = self.client.post("/api/v1/activity-types",
                                    headers=self.successops_token,
                                    content_type="application/json")

        message = "Data for creation must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_create_activity_type_missing_fields(self):
        """Test creation of new activity type fails with missing fields."""
        new_activity_type = dict(name="Blog Editor",
                                 value=1000)

        response = self.client.post("/api/v1/activity-types",
                                    data=json.dumps(new_activity_type),
                                    headers=self.successops_token,
                                    content_type="application/json")

        message = "required"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["description"][0])
        self.assertEqual(response.status_code, 400)

    def test_edit_activity_type(self):
        """Test editing of existing activity type is successful."""
        edit_activity_type = dict(name="Look at me",
                                  description="You think this is a game!!!",
                                  value=1000,
                                  supports_multiple_participants=False)

        response = self.client.put(
                        f"/api/v1/activity-types/{self.hackathon.uuid}",
                        data=json.dumps(edit_activity_type),
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Edit successful"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_edit_activity_type_no_payload(self):
        """Test editing of existing activity without payload fails."""
        response = self.client.put(
                        f"/api/v1/activity-types/{self.hackathon.uuid}",
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Data for editing must be provided."
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_edit_activity_type_no_ID(self):
        """Test editing of existing activity without ID fails."""
        edit_activity_type = dict(name="Look at me",
                                  description="You think this is a game!!!",
                                  value=1000)

        response = self.client.put(
                        "/api/v1/activity-types/",
                        data=json.dumps(edit_activity_type),
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Activity type to be edited must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_edit_nonexistent_activity_type(self):
        """Test editing of non-existent activity fails."""
        edit_activity_type = dict(name="Look at me",
                                  description="You think this is a game!!!",
                                  value=1000)

        response = self.client.put(
                        "/api/v1/activity-types/428080138-2303892",
                        data=json.dumps(edit_activity_type),
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Resource not found"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_get_activity_types(self):
        """Test retrieval of all activity types."""
        response = self.client.get('api/v1/activity-types',
                                   headers=self.header)

        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.get_data(as_text=True))
        activity_types = ActivityType.query.all()

        # test that response data matches database
        self.assertEqual(len(activity_types), len(response_content['data']))

    def test_get_activity_type_by_id(self):
        """Test retrieval of a single activity type by ID."""
        response = self.client.get(
                    f'api/v1/activity-types/{self.hackathon.uuid}',
                    headers=self.header)

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_activity_type_by_name(self):
        """Test retrieval of a single activity type by name."""
        response = self.client.get(
                    f'api/v1/activity-types?q={self.hackathon.name}',
                    headers=self.header)

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_delete_activity_type(self):
        """Test deletion of existing activity type is successful."""
        response = self.client.delete(
                        f"/api/v1/activity-types/{self.hackathon.uuid}",
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "deleted successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_delete_activity_type_no_id(self):
        """Test deletion of activity type with no ID unsuccessful."""
        response = self.client.delete(
                        f"/api/v1/activity-types",
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Activity type must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_delete_nonexistent_activity_type(self):
        """Test deletion of non-existing activity type is unsuccessful."""
        response = self.client.delete(
                        "/api/v1/activity-types/389139831-193831",
                        headers=self.successops_token,
                        content_type="application/json"
                        )

        message = "Resource not found"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)
