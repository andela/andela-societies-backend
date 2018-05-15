"""Module to house setup, teardown and utility class for testing."""

import os
import datetime
import base64
from unittest import TestCase

from api.models import (Activity, ActivityType, Cohort, Country,
                        LoggedActivity, Society, User, Role, db)
from app import create_app
from jose import jwt


class BaseTestCase(TestCase):
    """Contain utility required for testing."""

    exp_date = datetime.datetime.utcnow()
    test_user_payload = {
        "UserInfo": {
            "email": "test.user.societies@andela.com",
            "first_name": "Test",
            "id": "-KdQsMt2U0ixIy_-yWTSZ",
            "last_name": "User",
            "name": "Test User",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-KXGy1EB1oimjQgFim6C"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    test_user2_payload = {
        "UserInfo": {
            "email": "test.user2.societies@andela.com",
            "first_name": "Test",
            "id": "-KdQsawesome_useridZ",
            "last_name": "User2",
            "name": "Test User2",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    test_successops_payload = {
        "UserInfo": {
            "email": "test.test@andela.com",
            "first_name": "test",
            "id": "-Ktest_id",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Success Ops": "-KkLwgbeJUO0dQKsEk1i"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
        }

    test_auth_role_payload = {
        "UserInfo": {
            "email": "test.test@andela.com",
            "first_name": "test",
            "id": "-Ktest_id",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Learning Facilitator": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    expired_payload = {
        "UserInfo": {
            "email": "test.test@andela.com",
            "first_name": "test",
            "id": "-Ktest_id",
            "last_name": "test",
            "name": "Test User",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date - datetime.timedelta(days=1)
    }

    incomplete_payload = {
        "UserInfo": {
            "first_name": "test",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    def setUp(self):
        """Setup function to configure test enviroment."""
        self.app = create_app("Testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        # test client
        self.client = self.app.test_client()

        self.header = {
            "Authorization": self.generate_token(self.test_user_payload),
            "Content-Type": "application/json"
        }
        self.success_ops = {
            "Authorization": self.generate_token(self.test_successops_payload)
            }
        self.bad_token_header = {
            "Authorization": self.generate_token(
                {"I don't know": "what to put here"}
            )
        }

        # test countries
        self.kenya = Country(name='Kenya')
        self.uganda = Country(name='Uganda')
        self.nigeria = Country(name='Nigeria')

        # test societies
        self.phoenix = Society(name="Phoenix",
                               color_scheme="#00001",
                               logo="https://bit.ly/2FTjkbV",
                               photo="https://bit.ly/2k2l0qx")
        self.istelle = Society(name="iStelle",
                               color_scheme="#00002",
                               logo="https://bit.ly/2FTjkbV",
                               photo="https://bit.ly/2k2l0qx")
        self.sparks = Society(name="Sparks",
                              color_scheme="#00003",
                              logo="https://bit.ly/2FTjkbV",
                              photo="https://bit.ly/2k2l0qx")
        self.invictus = Society(name="Invictus",
                                color_scheme="#00004",
                                logo="https://bit.ly/2FTjkbV",
                                photo="https://bit.ly/2k2l0qx")

        # test roles
        self.successops_role = Role(uuid="-KkLwgbeJUO0dQKsEk1i",
                                    name="Success Ops")
        self.fellow_role = Role(uuid="-KXGy1EB1oimjQgFim6C", name="Fellow")
        self.success_role = Role(uuid="-KXGy1EB1oimjQgFim6F", name="Success")
        self.finance_role = Role(uuid="-KXGy1EB1oimjQgFim6L", name="Finance")
        self.lf_role = Role(uuid="d47ec8a7-3f09-44a5-8188-ff1d40ef35b6",
                            name="Learning Facilitator")

        # test cohorts
        self.cohort_12_Ke = Cohort(name="cohort-12", country=self.kenya)
        self.cohort_12_Ug = Cohort(name="cohort-12", country=self.uganda)
        self.cohort_1_Nig = Cohort(name="cohort-1", country=self.nigeria)

        # test users
        self.test_user = User(
            uuid="-KdQsMt2U0ixIy_-yWTSZ",
            name="Test User",
            photo="https://www.link.com",
            email="test.user.societies@andela.com",
            country=self.nigeria,
            cohort=self.cohort_1_Nig,
            society=self.phoenix)

        self.test_user_2 = User(
            uuid="-KdQsawesome_useridZ",
            name="Test User2",
            photo="https://www.link.com",
            email="test.user2.societies@andela.com",
            country=self.uganda,
            cohort=self.cohort_12_Ug,
            society=self.sparks
        )

        self.president = User(
            uuid="-KdQsMtixG4U0y_-yJEH",
            name="Test President",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
            email="test.president.societies@andela.com",
            country=self.kenya,
            cohort=self.cohort_12_Ke,
            society=self.phoenix
        )

        # test ActivityType
        self.hackathon = ActivityType(name="Hackathon",
                                      description="A Hackathon",
                                      value=100)
        self.tech_event = ActivityType(name="Tech Event",
                                       description="Organize a tech event",
                                       value=2500)
        self.interview = ActivityType(
            name="Bootcamp Interviews",
            description="Interviewing candidate for a fellow"
            " recruiting event",
            value=20
        )

        # test Activity
        self.alibaba_ai_challenge = Activity(
            name='Fashion challenge',
            activity_type=self.hackathon,
            activity_date=datetime.date.today() + datetime.timedelta(days=21),
            added_by=self.president
        )
        self.js_meet_up = Activity(
            name='Nairobi Js meetup',
            activity_type=self.tech_event,
            activity_date=datetime.date.today() + datetime.timedelta(days=14),
            added_by=self.president
        )
        self.bootcamp_xiv = Activity(
            name='Bootcamp XIV Interviews - Kenya',
            activity_type=self.interview,
            activity_date=datetime.date.today() + datetime.timedelta(days=14),
            added_by=self.president
        )

        # test LoggedActivity
        self.log_alibaba_challenge = LoggedActivity(
            name="my logged activity",
            description="Participated in this event",
            value=2500,
            user=self.test_user,
            activity=self.alibaba_ai_challenge,
            society=self.phoenix,
            activity_type=self.hackathon
        )

        # save common items to db
        self.tech_event.save()
        self.interview.save()
        self.hackathon.save()
        self.test_user.save()

    @staticmethod
    def generate_token(payload):
        """Generate token."""
        env_key = os.environ['PRIVATE_KEY_TEST']
        decoded_key = base64.b64decode(env_key).decode("utf-8")
        token = jwt.encode(payload, decoded_key, algorithm="RS256")
        return token

    def tearDown(self):
        """Clean up after every test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
