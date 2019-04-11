"""Log Activity Test Suite."""
import datetime
import json

from .base_test import BaseTestCase


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

    def test_log_activity_type_that_supports_multi_participants(self):
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

        data['noOfParticipants'] = 5
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

        data['noOfParticipants'] = 5
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
    def test_fellow_level_information_is_present(self):
        """
        Test fellow D-level information is fetched in th user's logged activities.

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
        # test that response data matches database query results
        self.assertEqual(len(response_content), 9)
        self.assertIn('level', response_content)
        self.assertIn('usedPoints', response_content)
        self.assertIn('remainingPoints', response_content)
        