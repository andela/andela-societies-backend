import json

from .base_test import BaseTestCase


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
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid,
                                 self.log_alibaba_challenge2.uuid]
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
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid,
                                 self.log_alibaba_challenge2.uuid]
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
            loggedActivitiesIds=[self.log_alibaba_challenge.uuid,
                                 self.log_alibaba_challenge2.uuid]
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
        logged_activities_ids request payload is of type List.
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
            loggedActivitiesIds=['i' for count in range(0, 21)]
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'Sorry, you can not approve more than 20 logged_activities at a go'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 403)
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

        message = 'invalid logged_activities_ids or no pending logged activities'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_details['message'], message)

    def test_fails_when_logged_activities_key_not_in_payload(self):

        """
        Test a scenario where loggedActivitiesIds key not in payload request assuming
        and invalid key is provided
        """

        self.successops_role.save()

        self.payload = dict(
            loggedActivitiesId=['13567788', '235555666']
        )

        response = self.client.put(
           f'/api/v1/logged-activities/approve/',
           data=json.dumps(self.payload),
           headers=self.success_ops
        )

        message = 'loggedActivitiesIds is required'
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
           f'/api/v1/logged-activities/reject/{self.log_alibaba_challenge.uuid}',
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
           '/api/v1/logged-activities/reject/43kaa',
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
           f'/api/v1/logged-activities/reject/{self.log_alibaba_challenge.uuid}',
           headers=self.success_ops
        )

        message = 'This logged activity is either in-review, approved or already rejected'
        response_details = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_details['message'], message)
