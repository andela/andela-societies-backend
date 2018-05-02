import json

from .base_test import BaseTestCase

from api.models import Society


class SocietyBaseTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.society = Society(
            name="Phoenix",
            color_scheme="#333333",
            logo="https://logo.png",
            photo="http://photo.url2"
        )
        self.society2 = dict(
            name="Invictus",
            colorScheme="#333334",
            logo="https://logo2.png",
            photo="http://photo.url"
        )
        self.society.save()
        self.successops_role.save()
        self.fellow_role.save()
        self.success_role.save()
        self.finance_role.save()

    def test_society_saved_successfully(self):
        old_societies = Society.query.all()
        post_response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(self.society2),
            headers=self.success_ops,
            content_type='application/json'
        )
        response_details = json.loads(post_response.data)

        self.assertIn("Society created successfully", response_details["message"])
        self.assertEqual(post_response.status_code, 201)

        new_societies = Society.query.all()
        self.assertEqual(
            len(new_societies), len(old_societies) + 1
        )
