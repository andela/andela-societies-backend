"""Activity Types Test Suite."""
import json

from api.models import ActivityType
from tests.base_test import BaseTestCase


class ActivityTypesTestCase(BaseTestCase):
    """Test activity types endpoints."""

    def test_get_activity_types(self):
        """Test retrieval of activity types."""
        # add test activity types
        self.hackathon.save()
        self.tech_event.save()

        response = self.client.get('api/v1/activity-types',
                                   headers=self.header)

        # test that request was successful
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.get_data(as_text=True))
        activity_types = ActivityType.query.all()

        # test that response data matches database
        self.assertEqual(len(activity_types), len(response_content['data']))
