'''Scheduled tasks tests module'''
from .base_test import BaseTestCase
from ..api.utils.notifications.email_notices import mail_success_ops


class SuccessOpsWeeklyTaskTestCase(BaseTestCase):
    '''Test app scheduler'''

    def test_that_mail_success_ops_works(self):
        '''
        Test that the mail success ops scheduled task works
        '''
        self.assertFalse(mail_success_ops(self.app))

        self.successops_role.save()
        self.client.get(
            f'/api/v1/logged-activities?paginate=false',
            headers=self.success_ops
        )
        self.log_alibaba_challenge.status = 'pending'
        self.log_alibaba_challenge.save()

        self.assertTrue(mail_success_ops(self.app)[0])
