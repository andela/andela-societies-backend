"""Logged Activity Test Suite."""
import datetime
import json

from .base_test import BaseTestCase, LoggedActivity


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

    def test_get_all_paginated_logged_activities(self):
        """
        Test fetching all paginated logged activities.

        When this is done by an authenticated user it should not fail.
        """
        response = self.client.get(
            f'/api/v1/logged-activities',
            headers=self.header
        )

        # test that request was successful
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.get_data(as_text=True))
        logged_activities_count = LoggedActivity.query.limit(
            self.app.config['PAGE_LIMIT']
        ).count()

        # test that response data count matches database query count
        self.assertEqual(logged_activities_count,
                         response_content['data']['count'])

    def test_get_all_unpaginated_logged_activities(self):
        """
        Test fetching all unpaginated logged activities.

        When this is done by an authenticated user it should not fail.
        """
        response = self.client.get(
            f'/api/v1/logged-activities?paginate=false',
            headers=self.header
        )

        # test that request was successful
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.get_data(as_text=True))
        logged_activities_count = LoggedActivity.query.count()

        # test that response data count matches database query count and
        # page key doesn't exist
        with self.assertRaises(KeyError):
            response_content['data']['page']

        self.assertEqual(logged_activities_count,
                         response_content['data']['count'])

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
            f'/api/v1/logged-activity/verify/{uuid}',
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
            f'/api/v1/logged-activity/verify/{uuid}',
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
            f'/api/v1/logged-activity/verify/{uuid}',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        self.assertEqual(response.status_code, 400)

    def test_secretary_edit_non_existent_logged_activity(self):
        """Test edit non-existent activity returns 404"""
        payload = {'status': 'invalid'}

        response = self.client.put(
            f'/api/v1/logged-activity/verify/-KlHerwfafcvavefa',
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
            f'/api/v1/logged-activity/verify/-KlHerwfafcvavefa',
            data=json.dumps(payload),
            headers=self.society_secretary
        )

        response_payload = json.loads(response.data)
        self.assertEqual(response_payload.get('message'),
                         'status is required.')
        self.assertEqual(response.status_code, 400)


class LoggedActivityApprovalTestCase(BaseTestCase):
    """Test to check approval of Logged activities by success ops"""

    def test_approving_logged_activities_successful(self):

        """
        Test a scenario where approval for logged activities passes
        if the user is a successops.
        """

        self.successops_role.save()
        self.log_alibaba_challenge.status = 'pending'
        self.log_alibaba_challenge2.status = 'pending'
        self.log_alibaba_challenge.save()
        self.log_alibaba_challenge2.save()

        self.payload = dict(
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid, self.log_alibaba_challenge2.uuid]
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'Activity edited successfully'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_details['message'], message)
        self.assertEqual(response_details['data'][0]['status'], 'approved')


    def test_approving_logged_activities_unsuccessful(self):

        """
        Test a scenario where approval for logged activities fails
        if the user is not a successops.
        """

        self.successops_role.save()
        self.log_alibaba_challenge.status = 'pending'
        self.log_alibaba_challenge2.status = 'rejected'
        self.log_alibaba_challenge.save()
        self.log_alibaba_challenge2.save()

        self.payload = dict(
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid, self.log_alibaba_challenge2.uuid]
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.header
        )

        message = 'You\'re unauthorized to perform this operation'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_details['message'], message)


    def test_approving_logged_activities_empty_request_fails(self):

        """
        Test a scenario where approval for logged activities passes
        if the user is a successops.
        """

        self.successops_role.save()

        self.payload = dict(
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid, self.log_alibaba_challenge2.uuid]
        )

        response = self.client.put(
           '/api/v1/logged-activities/approve/',
           headers=self.success_ops
        )

        message = 'Data for creation must be provided.'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_details['message'], message)


    def test_approving_logged_activities_id_is_string_fails(self):

        """
        Test a scenario where approval for logged activities fails when
        logged_activities_ids request payload is of type string.
        """

        self.successops_role.save()
        self.payload = dict(
            loggedActivitiesIds='400404004040'
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'A List/Array with at least one logged activity id is needed!'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_details['message'], message)


    def test_approving_over_twenty_logged_activities_fails(self):

        """
        Test a scenario where approval for logged activities fails
        if logged activities request is more than 20.
        """

        self.successops_role.save()
        self.payload = dict(
            status='approved',
            loggedActivitiesIds=['i' for count in range(0,21)]
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'Sorry, you can not approve more than 20 logged_activities at a go'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response_details['message'], message)


    def test_approving_when_all_logged_activities_invalid_fails(self):

        """
        Test a scenario where approval for logged activities fails
        when logged_activities_id supplied are invalid or are not
        in pending state
        """

        self.successops_role.save()

        self.payload = dict(
            loggedActivitiesIds=['13567788', '235555666']
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'Invalid logged activities or no pending logged activities in request'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_details['message'], message)


class LoggedActivityRejectTestCase(BaseTestCase):
    """Test to check rejection of Logged activities by success ops"""


    def test_reject_logged_activities_successful(self):

        """
        Test a scenario where rejection of a logged activity passes
        if the user is a successops.
        """

        self.successops_role.save()
        self.log_alibaba_challenge.status = 'pending'
        self.log_alibaba_challenge.save()

        response = self.client.put(
           f'/api/v1/logged-activity/reject/{self.log_alibaba_challenge.uuid}',
           headers=self.success_ops
        )

        message = 'Activity successfully rejected'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_details['message'], message)
        self.assertEqual(response_details['data']['status'], 'rejected')


    def test_reject_invalid_logged_activities_unsuccessful(self):

        """
        Test a scenario where rejection of a logged activity fails
        if logged activity doesn't exit.
        """

        self.successops_role.save()

        response = self.client.put(
           '/api/v1/logged-activity/reject/43kaa',
           headers=self.success_ops
        )

        message = 'Logged activity not found'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_details['message'], message)

    def test_reject_non_pending_logged_activities_unsuccessful(self):

        """
        Test a scenario where rejection of a logged activity fails
        if logged activity status is not pending.
        """

        self.successops_role.save()
        self.log_alibaba_challenge.status = 'rejected'
        self.log_alibaba_challenge.save()

        response = self.client.put(
           f'/api/v1/logged-activity/reject/{self.log_alibaba_challenge.uuid}',
           headers=self.success_ops
        )

        message = 'This logged activity is either in-review, approved or already rejected'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response_details['message'], message)

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
