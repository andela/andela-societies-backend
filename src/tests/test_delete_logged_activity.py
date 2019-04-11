import json

from .base_test import BaseTestCase, LoggedActivity


class DeleteLoggedActivityTestCase(BaseTestCase):
    """Delete logged activity test cases."""

    def test_logged_activity_deleted_successfully(self):
        """Test that a logged activity was deleted successfully."""
        self.log_alibaba_challenge.save()

        logged_activity = LoggedActivity.query.filter_by(
            name='my logged activity').first()

        response = self.client.delete(
            '/api/v1/logged-activities/' + logged_activity.uuid,
            headers=self.header
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistent_logged_activity(self):
        """Test a scenario where a logged activity
        to be deleted does not exist.
        """
        message = 'Logged Activity does not exist!'
        logged_activity_id = 'qwerfdse-23232-ucvhh-1233'
        response = self.client.delete(
            '/api/v1/logged-activities/'+logged_activity_id,
            headers=self.header
        )

        self.assertTrue(response.status_code == 404)
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(message, response_details['message'])

    def test_delete_nonpending_logged_activity(self):
        """Test a scenario where a logged activity
        to be deleted does not exist.
        """
        message = 'You are not allowed to perform this operation'
        self.log_alibaba_challenge.status = 'approved'
        self.log_alibaba_challenge.save()

        response = self.client.delete(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            headers=self.header
        )

        self.assertEqual(response.status_code, 403)
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(message, response_details['message'])
