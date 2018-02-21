import json

from .base_test import BaseTestCase

from api.models import Society


class SocietyTestCase(BaseTestCase):
    
    def test_society_saved_successfully(self):
        new_society = dict(
            name="Invictus",
            colorScheme="#333334",
            logo="https://logo2.png",
            photo="http://photo.url"
        )

        old_societies = Society.query.all()
        post_response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(new_society),
            content_type='application/json'
        )

        new_societies = Society.query.all()
    
        self.assertEqual(
            len(new_societies), len(old_societies) + 1
        )
