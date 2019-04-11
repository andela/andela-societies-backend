"""Test suite for Point Redemption Module."""
import json
import uuid

from .points_redemption_base_test_case_setup import PointRedemptionBaseTestCase


class EditRedemptionRequest(PointRedemptionBaseTestCase):

    def test_edit_redemption_request(self):
        """Test edit of Redemption Request through endpoint."""
        edit_request = dict(
            name="T-shirt Funds Request",
            value=2500
        )

        response = self.client.put(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            data=json.dumps(edit_request),
            headers=self.society_president,
            content_type='application/json')

        message = "edited successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_edit_delete_non_pending_redemption_request(self):
        """
        Test edit and deletion of Redemption Request when it's no
        longer pending fails
        """
        edit_request = dict(
            name="T-shirt Funds Request",
            value=2500
        )
        self.redemp_req.status = 'approved'
        self.redemp_req.save()

        response = self.client.put(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            data=json.dumps(edit_request),
            headers=self.society_president,
            content_type='application/json')

        message = "already approved or rejected"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.society_president
        )
        response_details = json.loads(response.data)
        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 403)

    def test_edit_nonexistent_redemption_request(self):
        """Test editing nonexistent Redemption Request fails."""
        edit_request = dict(
            name="T-shirt Funds Request",
            value=2500
        )

        response = self.client.put(
            f"api/v1/societies/redeem/{str(uuid.uuid4())}",
            data=json.dumps(edit_request),
            headers=self.society_president,
            content_type='application/json')

        message = "does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_edit_redemption_request_no_id(self):
        """Test editing request without ID fails."""
        edit_request = dict(
            name="T-shirt Funds Request",
            value=2500
        )

        response = self.client.put("api/v1/societies/redeem",
                                   data=json.dumps(edit_request),
                                   headers=self.society_president,
                                   content_type='application/json')

        message = "Redemption Request to be edited must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_edit_redemption_request_no_payload(self):
        """Test editing request without payload fails."""
        response = self.client.put(f"api/v1/societies/redeem/{self.sparks.uuid}",
                                   headers=self.society_president,
                                   content_type='application/json')

        message = "Data for editing must be provided"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 400)
