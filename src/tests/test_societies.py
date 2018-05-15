"""Test suite for Society Module."""
import json
import uuid
from app import create_app
from .base_test import BaseTestCase
from api.models import Society, Role, db


class SocietyBaseTestCase(BaseTestCase):
    """Test class for Society Module including endpoint."""

    def setUp(self):
        """Set up all needed variables."""
        BaseTestCase.setUp(self)
        self.successops_role.save()
        self.society = Society(
            name="Phoenix",
            color_scheme="#333333",
            logo="https://logo.png",
            photo="http://photo.url2"
        )
        self.society2 = dict(
            name="Invictus",
            colorScheme="#333334",
            logo="https://logo2.png",
            photo="http://photo.url"
        )
        self.society3 = dict(
            name="Stacked Deck",
            logo="https://logo2.png",
            photo="http://photo.url"
        )
        self.invictus.save()
        self.istelle.save()
        self.sparks.save()
        self.phoenix.save()
        self.society.save()

    def test_create_society(self):
        """Test new society saved successfully."""
        post_response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(self.society2),
            headers=self.success_ops,
            content_type='application/json'
        )
        self.assertEqual(post_response.status_code, 201)

        message = "Society created successfully"
        response_details = json.loads(post_response.data)

        self.assertIn(message, response_details["message"])

    def test_create_society_no_payload(self):
        """Test Society creation fails without payload."""
        response = self.client.post('/api/v1/societies',
                                    headers=self.success_ops,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)

        message = "Data for creation must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])

    def test_create_society_missing_field(self):
        """Test new society saved successfully."""
        response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(self.society3),
            headers=self.success_ops,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        message = "Name, color scheme and logo are required"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])

    def test_get_society_by_id(self):
        """Test a society can be retrieved by ID."""
        response = self.client.get(f"api/v1/societies/{self.sparks.uuid}",
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_society_by_name(self):
        """Test a society can be retrieved by name."""
        response = self.client.get(f"api/v1/societies?q={self.istelle.name}",
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_all_societies(self):
        """Test all societies are retrieved."""
        response = self.client.get("api/v1/societies",
                                   headers=self.header,
                                   content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_edit_society_details(self):
        """Test editing society details is successful."""
        society_details = dict(name="Stacked Deck",
                               colorScheme="#39ff14",
                               logo="https://bit.ly/2ImtzlI",
                               photo="https://bit.ly/2GlwdjF2E")

        response = self.client.put(f"api/v1/societies/{self.istelle.uuid}",
                                   data=json.dumps(society_details),
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "edited successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_edit_nonexistent_society(self):
        """Test editing nonexistent society fails."""
        society_details = dict(name="Stacked Deck",
                               colorScheme="#39ff14",
                               logo="https://bit.ly/2ImTzlI",
                               photo="https://bit.ly/2GliF2E")

        response = self.client.put(f"api/v1/societies/{str(uuid.uuid4())}",
                                   data=json.dumps(society_details),
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "Society does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_edit_society_no_id(self):
        """Test editing request without ID fails."""
        society_details = dict(name="Stacked Deck",
                               colorScheme="#39ff14",
                               logo="https://bit.ly/2ImTzlI",
                               photo="https://bit.ly/2GliF2E")

        response = self.client.put("api/v1/societies",
                                   data=json.dumps(society_details),
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "Society to be edited must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_edit_society_no_payload(self):
        """Test editing request without payload fails."""
        response = self.client.put(f"api/v1/societies/{self.sparks.uuid}",
                                   headers=self.success_ops,
                                   content_type='application/json')

        message = "Data for editing must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_delete_society(self):
        """Test deletion of society is successful."""
        response = self.client.delete(f"api/v1/societies/{self.phoenix.uuid}",
                                      headers=self.success_ops,
                                      content_type='application/json')

        message = "deleted successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_society(self):
        """Test deletion of non-existent society fails."""
        response = self.client.delete("api/v1/societies/801029-203191-023032",
                                      headers=self.success_ops,
                                      content_type='application/json')

        message = "does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_delete_society_no_id(self):
        """Test deletion request rejected with no ID provided."""
        response = self.client.delete("api/v1/societies",
                                      headers=self.success_ops,
                                      content_type='application/json')

        message = "Society id must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)


class SocietyTestCaseEmpty(BaseTestCase):
    """Test case for no societies in DB."""

    def setUp(self):
        """Set up all needed variables."""
        self.app = create_app("Testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.successops_role = Role(uuid="-KkLwgbeJUO0dQKsEk1i",
                                    name="Success Ops")
        self.successops_role.save()
        # test client
        self.client = self.app.test_client()

        self.header = {
            "Authorization": self.generate_token(self.test_user_payload),
            "Content-Type": "application/json"
        }

    def test_get_all_societies_empty(self):
        """Test lack of societies in system is returned."""
        response = self.client.get("api/v1/societies",
                                   headers=self.header,
                                   content_type='application/json')

        message = "Resources were not found"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)
