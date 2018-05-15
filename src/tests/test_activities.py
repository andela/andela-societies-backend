"""Tests for Activities Module."""
import json
import datetime
from api.models import ActivityType
from tests.base_test import BaseTestCase


class ActivitiesTestCase(BaseTestCase):
    """Test activities endpoints."""

    def setUp(self):
        """Save required roles."""
        BaseTestCase.setUp(self)
        self.successops_role.save()
        self.fellow_role.save()
        self.successops_token =\
            {"Authorization":
                self.generate_token(self.test_successops_payload)}

    def test_create_activity(self):
        """Test that an activity has been created successfully."""
        new_activity = dict(name="tech congress",
                            description="all about tech",
                            activityTypeId=self.get_activity_type_id(
                                "Tech Event"),
                            activityDate=str(datetime.date.today()))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)

        message = "Activity created successfully."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])

    def test_create_activity_no_payload(self):
        """Test when no payload has been passed it fails cleanly."""
        response = self.client.post('/api/v1/activities',
                                    headers=self.successops_token,
                                    content_type='application/json')

        message = "Data for creation must be provided."
        response_details = json.loads(response.data)

        self.assertEqual(message, response_details["message"])
        self.assertEqual(response.status_code, 400)

    def test_description_not_given(self):
        """Test for where description isn't provided in request object."""
        new_activity = dict(name="hackathon",
                            activityTypeId=self.get_activity_type_id(
                                "Tech Event"),
                            activityDate=str(datetime.date.today()))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 400)

        message = 'A description is required.'

        self.assertEqual(message, response_details['description']['message'])

    def test_name_not_given(self):
        """Test for where name is not provided in request object."""
        new_activity = dict(description="all about tech",
                            activityDate=str(datetime.date.today()))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 400)

        message = 'A name is required.'

        self.assertEqual(message, response_details['name']['message'])

    def test_save_existing_activity(self):
        """Test attempt to save an already existing activity."""
        # store activity to the database
        self.js_meet_up.save()

        existing_activity = dict(
            name="Nairobi Js meetup",
            description="all about js",
            activityTypeId=self.get_activity_type_id(
                "Tech Event"),
            activityDate=str(datetime.date.today()))

        # attempt to save the already existing activity
        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(existing_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')
        message = "Activity already exists!"

        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 409)

        self.assertEqual(message, response_details["name"])

    def test_non_existent_activity_type(self):
        """Test if activity type does not exist."""
        new_activity = dict(name="Tech Festival",
                            description="learn new things in tech",
                            activityTypeId=(
                                "da6321920@#$$911e8691232c4b301d34123"),
                            activityDate=str(datetime.date.today()))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')
        message = "Activity type does not exist or is unsupported."
        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 404)

        self.assertEqual(message, response_details["activity_type_id"])

    def test_activity_date_not_given(self):
        """Test of activity date is not provided."""
        new_activity = dict(name="tech congress",
                            description="all about tech",
                            activityTypeId=self.get_activity_type_id(
                                "Tech Event"))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        message = "An activity date is required."
        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 400)

        self.assertEqual(message, response_details["activityDate"]["message"])

    def test_past_activity_date(self):
        """Test if activity date given is in the past."""
        new_activity = dict(name="tech congress",
                            description="all about tech",
                            activityTypeId=self.get_activity_type_id(
                                "Tech Event"),
                            activityDate="2016-1-20")

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        message = "Date is in the past! Please enter a valid date."
        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 400)

        self.assertEqual(message, response_details["activity_date"]["message"])

    def test_activity_is_invalid(self):
        """Test if the activity name given is a valid activity."""
        new_activity = dict(name="Open Source App",
                            description="open source project",
                            activityTypeId=self.get_activity_type_id(
                                "Tech Event"),
                            activityDate=str(datetime.date.today()))

        response = self.client.post('/api/v1/activities',
                                    data=json.dumps(new_activity),
                                    headers=self.successops_token,
                                    content_type='application/json')

        message = 'This is not a valid activity!'
        response_details = json.loads(response.data)

        self.assertEqual(response.status_code, 400)

        self.assertEqual(message, str(response_details['name']))

    @staticmethod
    def get_activity_type_id(name):
        """Get activity type id using its name."""
        activity_type = ActivityType.query.filter_by(
                        name=name).first()
        activity_type_id = activity_type.uuid

        return activity_type_id
