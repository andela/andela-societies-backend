'''Module containing tasks helpers tests'''
from .base_test import BaseTestCase
from ..api.services.notifications.helpers import \
    generate_success_ops_pending_activities_emails


class HelpersTestCase(BaseTestCase):
    '''Test Class for helper functions'''

    def test_when_no_succes_ops_role_exists(self):
        '''Check that no emails are genrated when no success ops role exists'''

        self.assertFalse(
            generate_success_ops_pending_activities_emails(self.app)
        )

    def test_when_there_are_no_pending_logged_activities(self):
        '''
        Check that no email is generated when there are no pending
        logged activities
        '''
        self.successops_role.save()
        self.client.get(
            f'/api/v1/logged-activities?paginate=false',
            headers=self.success_ops
        )
        self.assertFalse(
            generate_success_ops_pending_activities_emails(self.app)
        )

    def test_successful_success_ops_mail_generation(self):
        '''
        Check that emails are generated when there are pending logged activities
        '''

        self.successops_role.save()
        self.client.get(
            f'/api/v1/logged-activities?paginate=false',
            headers=self.success_ops
        )
        self.log_alibaba_challenge.status = 'pending'
        self.log_alibaba_challenge.save()

        self.assertTrue(
            generate_success_ops_pending_activities_emails(self.app)[0]
        )
        self.assertIn(
            self.test_successops_payload['UserInfo']['name'],
            generate_success_ops_pending_activities_emails(
                self.app)[1][0]['message']
        )
