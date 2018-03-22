"""
Sample Data for Initial Run.

This contains the sample initial data required for the test run of the system.
"""
from api.models import (ActivityType, Activity, Country, LoggedActivity,
                        Society, User, Role)

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

# societies
phoenix = Society(name="Phoenix")
istelle = Society(name="iStelle")
sparks = Society(name="Sparks")
invictus = Society(name="Invictus")

# test countries
kenya = Country(name='Kenya')

# roles available
role = [Role(uuid="-KXGy1EB1oimjQgFim6F", name="Success"),
        Role(uuid="-KXGy1EB1oimjQgFim6L", name="Finance"),
        Role(uuid="-KXGy1EB1oimjQgFim6C", name="Fellow"),
        Role(uuid="-KkLwgbeJUO0dQKsEk1i", name="Success Ops"),
        Role(uuid="-KiihfZoseQeqC6bWTau", name="Andelan")]

# test user
user = User(
    uuid="-KdQsMt2U0ixIy_-yJEH",
    name="Test User",
    photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
          "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
    email="lawrence.wachira@andela.com",
    country=kenya,
    society=phoenix
    )
user.roles.append(role[2])


# test activities
python_blog = Activity(name="TDD For The Lazy Programmer", activity_type=blog)
interview_2017 = Activity(name="2017-feb-bootcamp-17", activity_type=interview)
open_saturdays_2018 = Activity(name="2018-feb-meetup",
                               activity_type=open_saturdays)

user.activities.extend([python_blog, interview_2017, open_saturdays_2018])

# LoggingActivity
blog_points = LoggedActivity(value=blog.value,
                             activity=python_blog,
                             user=user)
interview_points = LoggedActivity(value=interview.value,
                                  activity=interview_2017,
                                  user=user)
open_saturday_points = LoggedActivity(value=open_saturdays.value,
                                      activity=open_saturdays_2018,
                                      user=user)


all_data = [interview, open_saturdays, tech_event, open_source, hackathon,
            blog, app, mentor, marketing, press, outside_mentoring, phoenix,
            istelle, sparks, invictus, user, blog_points, interview_points,
            open_saturday_points]
