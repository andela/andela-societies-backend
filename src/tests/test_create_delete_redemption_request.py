"""Test suite for Point Redemption Module."""
import json

from .points_redemption_base_test_case_setup import PointRedemptionBaseTestCase


class CreateDeleteRedemptionRequest(PointRedemptionBaseTestCase):
    """Test class for Society point redemption including endpoint."""

    def test_create_redemption_request(self):
        """Test creation of Redemption Request through endpoint."""
        self.phoenix._total_points = 5000
        self.lagos.save()

        new_request = dict(
            reason="T-shirt Funds Request",
            value=2500,
            user_id=self.test_user.uuid,
            center="Lagos"
        )

        response = self.client.post("api/v1/societies/redeem",
                                    data=json.dumps(new_request),
                                    headers=self.society_president,
                                    content_type='application/json')

        message = "created"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 201)

    def test_create_redemption_request_when_remaining_points_inadequate(self):
        """
        Test that creating a redemption request fails when a society
        does not have enough remaining points
        """
        self.lagos.save()

        new_request = dict(
            reason="T-shirt Funds Request",
            value=2500,
            user_id=self.test_user.uuid,
            center="Lagos"
        )

        response = self.client.post("api/v1/societies/redeem",
                                    data=json.dumps(new_request),
                                    headers=self.society_president,
                                    content_type='application/json')

        message = "Redemption request value exceeds your society's" \
                  " remaining points"
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 403)

    def test_create_redemption_request_no_payload(self):
        """Test RedemptionRequest creation without payload fails."""
        response = self.client.post("api/v1/societies/redeem",
                                    headers=self.society_president,
                                    content_type='application/json')

        message = "must have data"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_create_redemption_request_invalid_fields(self):
        """Test RedemptionRequest creation without payload fails."""
        invalid_request = dict(
            descriptor="T-shirt Funds Request",
            amount=2500,
            user_id=self.test_user.uuid
        )

        response = self.client.post("api/v1/societies/redeem",
                                    data=json.dumps(invalid_request),
                                    headers=self.society_president,
                                    content_type='application/json')

        message = "required"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["center"]["message"])
        self.assertEqual(response.status_code, 400)

    def test_delete_redemption_request(self):
        """Test deletion of Redemption Request is successful."""
        response = self.client.delete(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.success_ops,
            content_type='application/json'
        )

        message = "deleted successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_delete_redemption_request_by_different_society_president(self):
        """
        Test deletion of Redemption Request is unsuccessful when the request is
        made by a society president of a different society
        """
        # check that valid society president can delete
        response = self.client.delete(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.society_president
        )

        message = "deleted successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

        self.redemp_req.save()
        self.sparks_president.save()

        response = self.client.delete(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.sparks_society_president
        )

        message = "RedemptionRequest does not exist."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_redemption_request(self):
        """Test deletion of non-existent Redemption Request fails."""
        response = self.client.delete(
            "api/v1/societies/redeem/801029-203191-023032",
            headers=self.success_ops,
            content_type='application/json')

        message = "does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_delete_redemption_request_no_id(self):
        """Test deletion request rejected with no ID provided."""
        response = self.client.delete("api/v1/societies/redeem",
                                      headers=self.success_ops,
                                      content_type='application/json')

        message = "RedemptionRequest id must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)
