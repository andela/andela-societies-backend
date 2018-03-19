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
        self.new_society = dict(
            name="Invictus",
            colorScheme="#333334",
            logo="https://logo2.png",
            photo="http://photo.url"
        )
        self.society.save()

        # retrieve a single society by id
        self.existing_society = Society.query.filter_by(name='phenix').first()
        self.society_details = self.existing_society.serialize()

        self.api_response = self.client.get('/api/v1/societies/' +
                                            self.society_details['uuid'])

    def test_society_saved_successfully(self):
        """ test if a new society has been
        successfully created """
        old_societies = Society.query.all()
        post_response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(self.new_society),
            content_type='application/json'
        )
        new_societies = Society.query.all()
        self.assertEqual(
            len(new_societies), len(old_societies) + 1
        )

    def test_if_missing_society_details(self):
        """ checks for an instance when the required
        details aren't given when creating a new society """
        self.new_society = dict(
            name="",
            colorScheme="",
            logo="",
            photo=""
        )

        response = self.client.post(
            '/api/v1/societies/',
            data=json.dumps(self.new_society),
            content_type='application/json'
        )
        self.assertTrue(response.status_code == 400)

        response_information = json.loads(response.data)
        self.assertEqual(response_information['message'],
                         'Name, color scheme and logo are '
                         'required to create a society.')

    def test_get_all_societies(self):
        """ test if the API can retrieve all societies
        from the database """
        response = self.client.get('/api/v1/societies/')
        self.assertTrue(response.status_code == 200)

        societies = json.loads(response.data)
        self.assertEqual(len(societies['data']['societies']), 2)

    def test_get_society_by_id(self):
        """ test if the API can retrieve a society by its id """
        self.assertTrue(self.api_response.status_code == 200)

        response_details = json.loads(self.api_response.data)
        self.assertEqual(response_details['data']['createdAt'],
                         self.society_details['createdAt'])

    def test_for_non_existant_society(self):
        """ test for error messsage if API attempts to retrieve
        a society that does not exist in the database """
        response = self.client.get('/api/v1/societies/12345')
        self.assertTrue(response.status_code == 404)

        response_details = json.loads(response.data)
        self.assertEqual(response_details['message'],
                         'Specified society does not exist.')

    def test_societies_page_limit(self):
        """ test the page  limit of the list of societies"""
        page_limit = 1
        response = self.client.get('/api/v1/societies?limit=' +
                                   str(page_limit))

        self.assertTrue(response.status_code == 200)

        societies = json.loads(response.data)
        self.assertEqual(len(societies['data']['societies']), page_limit)

    def test_edit_society_details(self):
        """ test if society information can be edited via the API """
        society_update = dict(
            name='Wakanda',
            colorScheme=None,
            logo=None,
            photo=None
        )
        headers = {'content-type': 'application/json'}

        response = self.client.put('/api/v1/societies/' +
                                   self.society_details['uuid'],
                                   data=json.dumps(society_update),
                                   headers=headers)
        self.assertTrue(response.status_code == 200)

        updated_society = Society.query.get(self.society_details['uuid'])
        self.assertEqual(updated_society.name, society_update['name'])

    def test_society_deleted_successfully(self):
        """ test if a society has been deleted successfully """
        response = self.client.delete('/api/v1/societies/' +
        self.society_details['uuid'])
        self.assertTrue(response.status_code == 200)

        response_message = json.loads(response.data)
        self.assertEqual(response_message['message'], 'Society deleted successfully.')

    def test_delete_nonexistent_society(self):
        """test for an attempt to delete a society that does not exist """
        response = self.client.delete('/api/v1/societies/12345')
        self.assertTrue(response.status_code == 404)

        response_message = json.loads(response.data)
        self.assertEqual(response_message['message'], 'Society does not exist.')


