"""Logged Activity Test Suite."""
from api.models import LoggedActivity
import json
import datetime

from.base_test import BaseTestCase


class LoggedActivitiesTestCase(BaseTestCase):
    """Logged activities test cases."""

    def setUp(self):
        """Inherit parent tests setUp."""
        super().setUp()

        # add test users and logged activity
        self.test_user.save()
        self.test_user_2.save()
        self.log_alibaba_challenge.save()

    def test_get_logged_activities_by_user_id(self):
        """
        Test fetching a user's logged activities.

        When this is done by an authenticated user it should not fail.
        """
        test_user_id = self.test_user.uuid
        response = self.client.get(
            f'/api/v1/users/{test_user_id}/logged-activities',
            headers=self.header
        )

        # test that request was successful
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.get_data(as_text=True))
        logged_activities = LoggedActivity.query.filter_by(
            user_id=test_user_id).all()

        # test that response data matches database query results
        self.assertEqual(len(logged_activities), len(response_content['data']))

    def test_get_logged_activities_message_when_user_has_none(self):
        """
        Test that users with no logged activities get a helpful
        message in the response
        """
        response = self.client.get(
            f'/api/v1/users/{self.test_user_2.uuid}/logged-activities',
            headers=self.header
        )
        response_content = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(response_content['data']), 0)

        message = "There are no logged activities for that user."
        self.assertEqual(response_content['message'], message)

    def test_get_logged_activities_message_when_user_does_not_exist(self):
        """Test that a 404 error is thrown when a user does not exist."""
        response = self.client.get(
            '/api/v1/users/user_id/logged-activities',
            headers=self.header
        )
        response_content = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_content['message'], "User not found")
        self.assertEqual(response.status_code, 404)


class LogActivityTestCase(BaseTestCase):
    """Log activity test cases."""

    def test_log_activity_using_activity_uuid_is_successful(self):
        """Test that logging an activity with activity uuid works."""
        self.alibaba_ai_challenge.save()

        payload = json.dumps(
            dict(activityId=f'{self.alibaba_ai_challenge.uuid}')
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that request was successful
        self.assertEqual(response.status_code, 201)

        # test response message
        response_content = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            response_content['message'], 'Activity logged successfully'
        )

    def test_log_activity_using_activity_type_uuid_is_successful(self):
        """Test that logging an activity with activity_type uuid works."""
        self.hackathon.save()

        payload = json.dumps(
            dict(activityTypeId=f'{self.hackathon.uuid}')
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that request was unsuccessful due to lacking fields
        self.assertEqual(response.status_code, 400)

        payload = json.dumps(
            dict(
                activityTypeId=f'{self.hackathon.uuid}',
                date=str(datetime.date.today() - datetime.timedelta(days=5)),
                description='Describing this activity here...'
            )
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that request is now successful
        self.assertEqual(response.status_code, 201)

    def test_log_interview_activity_requires_no_of_interviewees(self):
        """
        Test that logging an interview activity fails
        without the no_of_interviewees field.
        """
        # using activity_type_id
        data = dict(
            activityTypeId=f'{self.interview.uuid}',
            date=str(datetime.date.today() - datetime.timedelta(days=5)),
            description='Describing this activity here...'
        )
        payload = json.dumps(data)
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 400
        self.assertEqual(response.status_code, 400)

        data['noOfInterviewees'] = 5
        payload = json.dumps(data)
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that request is now successful
        self.assertEqual(response.status_code, 201)

        # using activity_id
        data = dict(
            activityId=f'{self.bootcamp_xiv.uuid}',
            description='Describing this activity here...'
        )
        payload = json.dumps(data)
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 400
        self.assertEqual(response.status_code, 400)

        data['noOfInterviewees'] = 5
        payload = json.dumps(data)
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that request is now successful
        self.assertEqual(response.status_code, 201)

    def test_log_interview_activity_when_user_is_not_a_society_member(self):
        """
        Test that logging an activity fails when user is not a society member.
        """
        payload = json.dumps(
            dict(
                activityTypeId=f'{self.hackathon.uuid}',
                date=str(datetime.date.today() - datetime.timedelta(days=5)),
                description='Describing this activity here...'
            )
        )
        self.test_user.society = None
        self.test_user.save()
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 422
        self.assertEqual(response.status_code, 422)

        # check response message
        message = 'You are not a member of any society yet'
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['message'], message
        )

    def test_log_activity_with_invalid_activity_id(self):
        """
        Test that logging an activity fails when an invalid activity id is
        used.
        """
        payload = json.dumps(dict(activityId='invalid_id_yo'))

        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 422
        self.assertEqual(response.status_code, 422)

    def test_log_activity_with_invalid_activity_type_id(self):
        """
        Test that logging an activity fails when an invalid activity_type
        id is used.
        """
        payload = json.dumps(
            dict(
                activityTypeId='invalid_activity_type_id',
                date=str(datetime.date.today() - datetime.timedelta(days=5)),
                description='Describing this activity here...'
            )
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 422
        self.assertEqual(response.status_code, 422)

    def test_log_activity_with_invalid_activity_date(self):
        """
        Test that logging an activity fails when an invalid date id is used.
        """
        payload = json.dumps(
            dict(
                activityTypeId='invalid_activity_type_id',
                date=str(datetime.date.today() + datetime.timedelta(days=1)),
                description='Describing this activity here...'
            )
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 422
        self.assertEqual(response.status_code, 422)

    def test_log_expired_activity(self):
        """
        Test that logging an activity fails when an invalid date id is used.
        """
        payload = json.dumps(
            dict(
                activityTypeId=f'{self.hackathon.uuid}',
                date=str(datetime.date.today() - datetime.timedelta(days=31)),
                description='Describing this activity here...'
            )
        )
        response = self.client.post(
            'api/v1/logged-activities',
            headers=self.header, data=payload
        )

        # test that response status_code is 422
        self.assertEqual(response.status_code, 422)

        self.assertEqual(
            json.loads(response.get_data(as_text=True))['message'],
            'You\'re late. That activity happened more than 30 days ago'
        )


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


class DeleteLoggedActivityTestCase(BaseTestCase):
    """Delete logged activity test cases."""

    def test_logged_activity_deleted_successfully(self):
        """Test that a logged activity was deleted successfully."""
        self.log_alibaba_challenge.save()

        logged_activity = LoggedActivity.query.filter_by(
                          name='my logged activity').first()

        response = self.client.delete(
            '/api/v1/logged-activities/'+logged_activity.uuid,
            headers=self.header
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistant_logged_activity(self):
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
