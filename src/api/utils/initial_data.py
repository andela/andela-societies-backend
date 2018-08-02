"""Sample Data for Initial Run.

This contains the sample initial data required for the test run of the system.
"""
import datetime
import os
import base64
import requests
from jose import jwt


from api.models import (ActivityType, Activity, Center, LoggedActivity,
                        Society, User, Cohort, Role)

# test centers
kenya = Center(name='Kenya')
uganda = Center(name='Uganda')
nigeria = Center(name='Nigeria')
centers = [kenya, uganda, nigeria]

cohorts = []

# setup dev user info to access Andela API

authorization_token = os.environ.get('DEV_TOKEN')
url = os.environ.get('ANDELA_API_URL')
public_key_token = os.environ.get('PUBLIC_KEY')

if public_key_token and authorization_token and url:
    try:
        API_IDENTIFIER = "andela.com"
        AUTH0_DOMAIN = "accounts.andela.com"

        public_key = base64.b64decode(public_key_token).decode("utf-8")
        payload = jwt.decode(authorization_token,
                             public_key,
                             algorithms=['RS256'],
                             options={
                                 'verify_signature': True,
                                 'verify_exp': True
                             },
                             audience=API_IDENTIFIER,
                             issuer=AUTH0_DOMAIN)
        Bearer = 'Bearer '
        headers = {'Authorization': Bearer + authorization_token}

        cohort_data_response = requests.get(url + 'cohorts',
                                            headers=headers).json()
        location_data_response = requests.get(url + 'locations',
                                              headers=headers).json()
        # test centers
        locations = {}

        for location in location_data_response.get('values'):
            name = location.get("name")
            locations[name] = Center(name=name.lower(),
                                     uuid=location.get('id'))

        centers = list(locations.values())

        # test centers
        kenya = location.get('Nairobi') or location.get('nairobi')

        # cohorts
        cohorts = []
        for cohort_information in cohort_data_response.get('values'):
            name = cohort_information.get('name')
            center = locations.get(
                cohort_information.get('location').get('name'))
            cohort = Cohort(name=name.lower(),
                            uuid=cohort_information.get('id'),
                            center_id=center.uuid)
            cohorts.append(cohort)
    except Exception:
        print("Your initial dev-data, won't work...")


# activity types
interview = ActivityType(name="Bootcamp Interviews",
                         description="Interviewing candidate for a fellow"
                         " recruiting event",
                         value=20)
open_saturdays = ActivityType(name="Open Saturdays Guides",
                              description="Guide applicants with the"
                              " recruitment team during open Saturdays",
                              value=50)
tech_event = ActivityType(name="Tech Event",
                          description="Organize a tech event",
                          value=2500)
open_source = ActivityType(name="Open Source Project",
                           description="Starting an open source project which"
                           " has at least 40 stars from non-Andelans",
                           value=2500)
hackathon = ActivityType(name="Hackathon",
                         description="Participating in a Hackathon",
                         value=100)
blog = ActivityType(name="Blog",
                    description="Write a blog that is published on Andela's"
                    " website",
                    value=1000)
app = ActivityType(name="App",
                   description="Build an app that is marketed on Andela's"
                   " website",
                   value=10000)
mentor = ActivityType(name="Mentoring",
                      description="Mentor a prospect for Andela 21",
                      value=250)
marketing = ActivityType(name="Marketing",
                         description="Participating in an Andela marketing"
                         "  event with partners",
                         value=2000)
press = ActivityType(name="Press Interview",
                     description="Participating in a press interview for"
                     " Andela marketing",
                     value=3000)
outside_mentoring = ActivityType(name="External Mentoring",
                                 description="Mentoring students outside of"
                                 " Andela e.g. via SheLovesCode",
                                 value=250)
activity_types = [
    interview, open_saturdays, tech_event, open_source, hackathon, blog,
    app, mentor, marketing, press, outside_mentoring
]

# societies
phoenix = Society(name="phoenix")
istelle = Society(name="istelle")
sparks = Society(name="sparks")
invictus = Society(name="invictus")
societies = [phoenix, istelle, sparks, invictus]

# roles available
roles = [
    Role(uuid="-KXGy1EB1oimjQgFim6F", name="success"),
    Role(uuid="-KXGy1EB1oimjQgFim6L", name="finance"),
    Role(uuid="-KXGy1EB1oimjQgFim6C", name="fellow"),
    Role(uuid="-KkLwgbeJUO0dQKsEk1i", name="success ops"),
    Role(uuid="-KiihfZoseQeqC6bWTau", name="andelan"),
    Role(name="society president"),
    Role(name="society vice president"),
    Role(name="society secretary")
]


def test_dev_user_seed_data():

    # cohorts
    cohort_14_ke = Cohort(name='Cohort 14 Test', center=kenya)
    # users
    # member
    member = User(
        uuid="-KdQsMtixI2U0y_-yJEH",
        name="Test User",
        photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
              "AI/AAAAAAAAABc/ImeP_cAI/photo.jpg?sz=50",
        email="test.user.societies@andela.com",
        center=kenya,
        cohort=cohort_14_ke,
        society=phoenix
    )
    member.roles.append(roles[2])

    # president
    president = User(
        uuid="-KdQsMtixG4U0y_-yJEH",
        name="Test President",
        photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
              "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
        email="test.president.societies@andela.com",
        center=kenya,
        cohort=cohort_14_ke,
        society=phoenix
    )
    president.roles.append(roles[5])
    president.roles.append(roles[2])

    # success ops
    success_ops = User(
        uuid="-KdQsMtixG4U0y_-yJEF",
        name="Test success ops",
        photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
              "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
        email="test.successops.societies@andela.com",
        center=kenya
    )
    success_ops.roles.append(roles[3])

    return [member, president, success_ops]


def test_dev_activities_seed_data():
    member, president, success_ops = test_dev_user_seed_data()
    # test activities
    python_hackathon = Activity(
        name="Hacktober Fest", activity_type=hackathon,
        activity_date=datetime.date.today() + datetime.timedelta(days=7),
        added_by=president
    )
    interview_2017 = Activity(
        name="2017-feb-bootcamp-17", activity_type=interview,
        activity_date=datetime.date.today() + datetime.timedelta(days=14),
        added_by=president)
    open_saturdays_2018 = Activity(
        name="2018-feb-meetup", activity_type=open_saturdays,
        activity_date=datetime.date.today() + datetime.timedelta(days=21),
        added_by=president
    )

    member.activities.extend([python_hackathon, interview_2017,
                              open_saturdays_2018])

    # Logged Activities
    hackathon_points = LoggedActivity(
        value=hackathon.value,
        activity=python_hackathon,
        user=member, society=phoenix,
        activity_type=hackathon,
        status='approved', approver_id=success_ops.uuid,
        reviewer_id=president.uuid,
        activity_date=python_hackathon.activity_date
    )
    interview_points = LoggedActivity(
        value=interview.value * 5,
        activity=interview_2017,
        user=member, society=sparks,
        activity_type=interview,
        status='rejected', approver_id=success_ops.uuid,
        reviewer_id=president.uuid,
        activity_date=interview_2017.activity_date
    )
    open_saturday_points = LoggedActivity(
        value=open_saturdays.value,
        activity=open_saturdays_2018,
        user=member, society=invictus,
        activity_type=open_saturdays,
        activity_date=open_saturdays_2018.activity_date
    )
    return [hackathon_points, interview_points, open_saturday_points]


production_data = activity_types + centers + cohorts + roles + societies
