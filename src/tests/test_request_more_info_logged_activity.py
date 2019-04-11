import json

from .base_test import BaseTestCase


class RequestMoreInfoLoggedActivityTestCase(BaseTestCase):
    """Logged activities test cases."""

    def setUp(self):
        """Inherit parent tests setUp."""
        super().setUp()
        self.successops_role.save()

        # add test users and logged activity
        self.test_user.save()
        self.test_user_2.save()
        self.log_alibaba_challenge.save()

    def test_request_for_info_successful(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made it should not fail.
        """
        activity_id = self.log_alibaba_challenge.uuid
        info_payload = dict(comment="Kindly give more informaton.")
        response = self.client.put(
            f'/api/v1/logged-activities/info/{activity_id}',
            headers=self.success_ops,
            data=json.dumps(info_payload),
            content_type='application/json'
        )
        message = "successfully requested"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 200)

    def test_request_for_info_fails_without_payload(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made without content it should fail.
        """
        activity_id = self.log_alibaba_challenge.uuid

        response = self.client.put(
            f'/api/v1/logged-activities/info/{activity_id}',
            headers=self.success_ops,
            content_type='application/json'
        )
        message = "must be provided"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 400)

    def test_request_for_info_fails_without_loggedactivity_id(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made without LoggedActivity ID it should fail.
        """
        response = self.client.put(
            f'/api/v1/logged-activities/info',
            headers=self.success_ops,
            content_type='application/json'
        )
        message = "must be provided"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 400)

    def test_request_for_info_fails_for_nonexistent_loggedactivity(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made for a logged_activity that doesn't exist, it
        should fail.
        """
        info_payload = dict(comment="Kindly give more informaton.")

        response = self.client.put(
            f'/api/v1/logged-activities/info/201dj1jdd801hjdjdjd08d2h8if2hf',
            headers=self.success_ops,
            data=json.dumps(info_payload),
            content_type='application/json'
        )
        message = "not found"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 404)

    def test_request_for_info_fails_with_wrong_keys(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made it should fail when the context is provided
        with different keys.
        """
        activity_id = self.log_alibaba_challenge.uuid
        info_payload = dict(info="Kindly give more informaton.")
        response = self.client.put(
            f'/api/v1/logged-activities/info/{activity_id}',
            headers=self.success_ops,
            data=json.dumps(info_payload),
            content_type='application/json'
        )
        message = "must be provided"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 400)

    def test_request_for_info_fails_without_context(self):
        """
        Test requesting more informaton on a logged activity.

        When the request is made it should fail when the context is not
        provided.
        """
        activity_id = self.log_alibaba_challenge.uuid
        info_payload = {}
        response = self.client.put(
            f'/api/v1/logged-activities/info/{activity_id}',
            headers=self.success_ops,
            data=json.dumps(info_payload),
            content_type='application/json'
        )
        message = "must be provided"
        # test that request was successful
        response_content = json.loads(response.get_data(as_text=True))
        self.assertIn(message, response_content['message'])
        self.assertEqual(response.status_code, 400)
