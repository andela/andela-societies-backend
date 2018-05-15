"""
Sample Data for Initial Run.

This contains the sample initial data required for the test run of the system.
"""
import datetime

from api.models import (ActivityType, Activity, Country, LoggedActivity,
                        Society, User, Cohort, Role)

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
phoenix = Society(name="Phoenix")
istelle = Society(name="iStelle")
sparks = Society(name="Sparks")
invictus = Society(name="Invictus")
societies = [phoenix, istelle, sparks, invictus]

# test countries
kenya = Country(name='Kenya')
uganda = Country(name='Uganda')
nigeria = Country(name='Nigeria')
countries = [kenya, uganda, nigeria]

# cohorts
cohort_14_ke = Cohort(name='Cohort 14', country=kenya)

# roles available
roles = [Role(uuid="-KXGy1EB1oimjQgFim6F", name="Success"),
         Role(uuid="-KXGy1EB1oimjQgFim6L", name="Finance"),
         Role(uuid="-KXGy1EB1oimjQgFim6C", name="Fellow"),
         Role(uuid="-KkLwgbeJUO0dQKsEk1i", name="Success Ops"),
         Role(uuid="-KiihfZoseQeqC6bWTau", name="Andelan"),
         Role(name="Society President")]

# users
# member
member = User(
    uuid="-KdQsMtixI2U0y_-yJEH",
    name="Test User",
    photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
          "AI/AAAAAAAAABc/ImeP_cAI/photo.jpg?sz=50",
    email="test.user.societies@andela.com",
    country=kenya,
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
    country=kenya,
    cohort=cohort_14_ke,
    society=phoenix
)
president.roles.append(roles[5])

# success ops
success_ops = User(
    uuid="-KdQsMtixG4U0y_-yJEF",
    name="Test Success Ops",
    photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
          "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
    email="test.successops.societies@andela.com",
    country=kenya
)
success_ops.roles.append(roles[3])

users = [member, president, success_ops]

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
logged_activities = [hackathon_points, interview_points, open_saturday_points]


test_data = (activity_types + societies + users + logged_activities + countries
             + roles)
production_data = activity_types + countries + societies
