import datetime
import json

from .base_test import BaseTestCase, LoggedActivity

class EditLoggedActivityTestCase(BaseTestCase):
    """Edit activity test cases."""

    def setUp(self):
        """Inherit parent tests setUp."""
        super().setUp()

        # add tests logged activity and corresponding activity
        self.alibaba_ai_challenge.save()
        self.log_alibaba_challenge.save()
        self.js_meet_up.save()

        self.payload = dict(
            description="Participated in that event",
            activityId=self.js_meet_up.uuid
        )

    def test_edit_logged_activity_is_successful(self):
        """Test that editing a logged activity does not fail."""

        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 200)

        message = 'Activity edited successfully'
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['message'], message
        )

        edited_activity = LoggedActivity.query.get(
            self.log_alibaba_challenge.uuid
        )
        self.assertEqual(edited_activity.activity_id, self.js_meet_up.uuid)

    def test_edit_logged_activity_by_non_owner_is_unsuccessful(self):
        """
        Test that editing a logged activity that
        doesn't belong to you fails.
        """
        self.header["Authorization"] = self.generate_token(
            self.test_user2_payload
        )

        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_logged_activity_that_is_no_longer_pending(self):
        """
        Test that editing a logged activity that has been approved or rejected
        fails.
        """
        self.log_alibaba_challenge.status = 'approved'
        self.alibaba_ai_challenge.save()

        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 401)

    def test_edit_logged_activity_parser_works(self):
        """
        Test that during editing a logged activity, the marshamallow result
        parser works the same way it does while logging an activity.
        """
        self.js_meet_up.activity_date = datetime.date.today() - \
            datetime.timedelta(days=31)
        self.js_meet_up.save()

        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 422)
        message = 'You\'re late. That activity happened more than 30 days ago'
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['message'], message
        )

        self.payload['activityId'] = 'invalid_activity_id'
        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 422)
        message = 'Invalid activity id'
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['message'], message
        )

    def test_edit_logged_activity_validation_works(self):
        """
        Test that during editing a logged activity, validation via marshmallow
        works the same way it does while logging an activity.
        """
        self.payload['activityTypeId'] = 'blah blah'

        response = self.client.put(
            f'/api/v1/logged-activities/{self.log_alibaba_challenge.uuid}',
            data=json.dumps(self.payload), headers=self.header
        )

        self.assertEqual(response.status_code, 400)

    def test_secretary_edit_logged_activity_works(self):
        """Test secretaty can change status to pending."""
        payload = {'status': 'pending'}
        uuid = self.log_alibaba_challenge.uuid
        response = self.client.put(
            f'/api/v1/logged-activities/review/{uuid}',
            data=json.dumps(payload),
            headers=self.society_secretary
        )
        response_payload = json.loads(response.data)
        self.assertEqual(response_payload.get('data').get('status'),
                         payload.get('status'))
        self.assertEqual(response.status_code, 200)

    def test_secretary_edit_reject_activity_works(self):
        """Test secretary can change status to rejected."""
        payload = {'status': 'rejected'}
        uuid = self.log_alibaba_challenge.uuid

        response = self.client.put(
            f'/api/v1/logged-activities/review/{uuid}',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        response_payload = json.loads(response.data)
        self.assertEqual(response_payload.get('data').get('status'),
                         payload.get('status'))
        self.assertEqual(response.status_code, 200)

    def test_secretary_edit_invalid_input(self):
        """Test invalid input is rejected."""
        payload = {'status': 'invalid'}
        uuid = self.log_alibaba_challenge.uuid
        response = self.client.put(
            f'/api/v1/logged-activities/review/{uuid}',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        self.assertEqual(response.status_code, 400)

    def test_secretary_edit_non_existent_logged_activity(self):
        """Test edit non-existent activity returns 404"""
        payload = {'status': 'invalid'}

        response = self.client.put(
            '/api/v1/logged-activities/review/-KlHerwfafcvavefa',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        response_payload = json.loads(response.data)
        self.assertEqual(response_payload.get('message'),
                         'Logged activity not found')
        self.assertEqual(response.status_code, 404)

    def test_secretary_edit_logged_activity_empty_payload(self):
        """Test edit activity with empty payload returns 400"""
        payload = {}

        response = self.client.put(
            '/api/v1/logged-activities/review/-KlHerwfafcvavefa',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        response_payload = json.loads(response.data)
        self.assertEqual(response_payload.get('message'),
                         'status is required.')
        self.assertEqual(response.status_code, 400)
