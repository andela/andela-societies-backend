import os

from .base_test import BaseTestCase, ActivityType, Society, db
from ..api.utils.initial_data import generete_initial_data_run_time_env
from ..manage import seed


class ManagementCommandsTestCase(BaseTestCase):
    '''Test management commands'''

    def setUp(self):
        super().setUp()
        data = generete_initial_data_run_time_env()
        self.societies = data.get('societies')
        self.activity_types = data.get('activity_types')

    def test_that_seed_command_works_without_errors(self):
        '''Test that the `python manage.py seed command` works'''
        os.environ['APP_SETTINGS'] = 'Testing'
        db.drop_all()
        db.create_all()

        initial_activity_types_count = ActivityType.query.count()
        initial_societies_count = Society.query.count()

        # run seeding command
        seed()

        new_activity_types_count = ActivityType.query.count()
        new_societies_count = Society.query.count()

        self.assertEqual(
            new_activity_types_count,
            initial_activity_types_count + len(self.activity_types)
        )
        self.assertEqual(
            new_societies_count,
            initial_societies_count + len(self.societies)
        )

    def test_that_seed_command_fails_in_production_unless_flag_is_true(self):
        '''Test that the `python manage.py seed command` works'''
        os.environ['APP_SETTINGS'] = 'Production'
        db.drop_all()
        db.create_all()

        initial_activity_types_count = ActivityType.query.count()
        initial_societies_count = Society.query.count()

        # run seeding command
        with self.assertRaises(SystemExit):
            seed()

        new_activity_types_count = ActivityType.query.count()
        new_societies_count = Society.query.count()

        self.assertEqual(
            new_activity_types_count, initial_activity_types_count
        )
        self.assertEqual(new_societies_count, initial_societies_count)
