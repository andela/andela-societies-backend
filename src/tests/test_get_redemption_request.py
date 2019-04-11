"""Test suite for Point Redemption Module."""
import json
import uuid

from .points_redemption_base_test_case_setup import PointRedemptionBaseTestCase


class GetRedemptionRequest(PointRedemptionBaseTestCase):

    def test_get_all_redemption_requests(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get("api/v1/societies/redeem",
                                   headers=self.society_president,
                                   content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_all_redemption_requests_by_cio(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get("api/v1/societies/redeem?paginate=false",
                                   headers=self.cio,
                                   content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_existing_redemption_requests_by_id(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.society_president,
            content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_existing_redemption_requests_by_name(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?name={self.redemp_req.name}",
            headers=self.society_president,
            content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_existing_redemption_requests_by_society(self):
        """Test retrieval of Redemption Requests."""
        self.test_user.society.save()
        response = self.client.get(
            f"api/v1/societies/redeem?society={self.test_user.society.name}",
            headers=self.society_president,
            content_type='application/json')
        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_existing_redemption_requests_by_status(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?status={self.redemp_req.status}",
            headers=self.society_president,
            content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_existing_redemption_requests_by_center(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?center={self.redemp_req.center.name}",
            headers=self.society_president,
            content_type='application/json')

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_redemption_requests_by_id(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem/{str(uuid.uuid4())}",
            headers=self.society_president,
            content_type='application/json')
        message = "does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_get_non_existing_redemption_requests_by_name(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?name={str(uuid.uuid4())}",
            headers=self.society_president,
            content_type='application/json')

        message = "Resources were not found."
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_get_non_existing_redemption_requests_by_society(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?society={str(uuid.uuid4())}",
            headers=self.society_president,
            content_type='application/json')
        message = f'not found'
        response_details = json.loads(response.data)

        self.assertTrue(response_details["message"].find(message))
        self.assertEqual(response.status_code, 400)

    def test_get_non_existing_redemption_requests_by_status(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?status={str(uuid.uuid4())}",
            headers=self.society_president,
            content_type='application/json')

        message = "Resources were not found."
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_get_non_existing_redemption_requests_by_center(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem?center={str(uuid.uuid4())}",
            headers=self.society_president,
            content_type='application/json')

        message = "not found"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)
