"""Logged Activity Test Suite."""
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
