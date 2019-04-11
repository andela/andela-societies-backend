import json
import uuid

from .base_test import BaseTestCase


class PointRedemptionApprovalTestCase(BaseTestCase):
    """Test class for point redemption completion/approval/rejection."""

    def setUp(self):
        """Set up all needed variables."""
        BaseTestCase.setUp(self)
        self.president_role.save()
        self.v_president_role.save()
        self.successops_role.save()
        self.finance_role.save()
        self.invictus.save()
        self.istelle.save()
        self.sparks.save()
        self.phoenix.save()
        self.redemp_req.save()
        self.test_cio.save()

    def test_point_redemption_approval_successful(self):
        """Test approval of redemption request.

        When approved the value of the redemption request should reflect on the
        society._total_points.
        """
        approval_payload = dict(status="approved")

        response = self.client.put(
            f"api/v1/societies/redeem/verify/{self.redemp_req.uuid}",
            data=json.dumps(approval_payload),
            headers=self.success_ops,
            content_type='application/json'
        )

        message = "status changed to {}".format(approval_payload["status"])
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_point_redemption_rejection_successful(self):
        """Test rejection of redemption request.

        When rejected the value of the redemption request should not reflect on
        the society._total_points.
        """
        approval_payload = dict(status="rejected",
                                rejection="The request is outside the scope.")

        response = self.client.put(
            f"api/v1/societies/redeem/verify/{self.redemp_req.uuid}",
            data=json.dumps(approval_payload),
            headers=self.success_ops,
            content_type='application/json'
        )

        message = "status changed to {}".format(approval_payload["status"])
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_point_redemption_info_request_successful(self):
        """Test query of redemption request.

        When the redemption request is not clear the CIO may request for
        more information from the Society President.
        """
        approval_payload = dict(comment="I'm not sure I understand.")

        response = self.client.put(
            f"api/v1/societies/redeem/verify/{self.redemp_req.uuid}",
            data=json.dumps(approval_payload),
            headers=self.success_ops,
            content_type='application/json'
        )

        message = "status changed"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_point_redemption_details_by_finance(self):
        """Test retrieval of Redemption Requests."""
        response = self.client.get(
            f"api/v1/societies/redeem/{str(uuid.uuid4())}",
            headers=self.finance,
            content_type='application/json')
        message = "does not exist"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 404)

    def test_get_point_redemption_details_by_finance(self):
        """Test view of RedemptionRequest by finance.
        """

        response = self.client.get(
            f"api/v1/societies/redeem/{self.redemp_req.uuid}",
            headers=self.finance,
            content_type='application/json'
        )

        message = "fetched successfully"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)

    def test_point_redemption_completion_successful(self):
        """Test completion of RedemptionRequest.

        When a redemption request funds have been sent out the redemption
        reequest should be marked as completed.
        """
        completion_payload = dict(status="completed")

        response = self.client.put(
            f"api/v1/societies/redeem/funds/{self.redemp_req.uuid}",
            data=json.dumps(completion_payload),
            headers=self.finance,
            content_type='application/json'
        )

        message = "completed"
        response_details = json.loads(response.data)

        self.assertIn(message, response_details["message"])
        self.assertEqual(response.status_code, 200)
