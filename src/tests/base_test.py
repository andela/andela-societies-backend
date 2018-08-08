"""Module to house setup, teardown and utility class for testing."""

import base64
import datetime
import os
import sys
from unittest import TestCase, mock
from jose import jwt

try:
    from app import create_app
    from api.models import (Activity, ActivityType, Cohort, Center,
                            LoggedActivity, Society, User, Role,
                            RedemptionRequest,
                            db)
except ModuleNotFoundError:
    # this will enable us to run individual test files
    # pytest <path to file>
    # e.g pytest tests/test_logged_activities.py
    # Run individual test within class
    # e.g pytest <path to file>.py::ClassName::test_method_name

    sys.path.insert(0,
                    os.path.abspath(
                        os.path.join(os.path.dirname(__file__), '..')))

    from app import create_app
    from api.models import (Activity, ActivityType, Cohort, Center,
                            LoggedActivity, Society, User, Role,
                            RedemptionRequest,
                            db)


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
                    "success ops": "-KkLwgbeJUO0dQKsEk1i"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    test_finance_payload = {
        "UserInfo": {
            "email": "test.cio@andela.com",
            "first_name": "Test",
            "id": "-Ktest_id",
            "last_name": "Finance",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "finance": "-KXGy1EB1oimjQgFim6L"
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

    test_society_president_role_payload = {
        "UserInfo": {
            "email": "test.president.societies@andela.com",
            "first_name": "Test",
            "id": "-KdQsMtixG4U0y_-yJEH",
            "last_name": "President",
            "name": "Test President",
            "picture": "https://bit.ly/2MeuICK",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "society president": "-KXGyd2udi2"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    test_cio_role_payload = {
        "UserInfo": {
            "email": "test.president.societies@andela.com",
            "first_name": "Test",
            "id": "-KdQsMtixG4U0y_-yJEH",
            "last_name": "President",
            "name": "Test President",
            "picture": "https://bit.ly/2MeuICK",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "cio": "-KXGionceu24i2y"
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

    test_society_secretary_payload = {
        "UserInfo": {
            "email": "test.secretary.societies@andela.com",
            "first_name": "Test secretary",
            "id": "-Kuty7hryt8cbkc",
            "last_name": "secretary",
            "name": "Test secretary",
            "picture": "https://bit.ly/2MeuICK",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "society secretary": "-KXGy12odfn2idn"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    def setUp(self):
        """Configure test enviroment."""
        os.environ['APP_SETTINGS'] = 'Testing'

        self.patcher = mock.patch('api.utils.auth.add_extra_user_info',
                                  return_value=(None, None, None))
        self.patcher.start()

        self.app = create_app("Testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        # test client
        self.client = self.app.test_client()

        token_payloads_list = [
             self.incomplete_payload,
             self.expired_payload,
             self.test_cio_role_payload,
             self.test_society_president_role_payload,
             self.test_auth_role_payload,
             self.test_finance_payload
        ]

        for token_payload in token_payloads_list:
            token_payload.update({
                'iss': self.app.config['API_ISSUER'],
                'aud': self.app.config['API_AUDIENCE']
            })

        self.header = {
            "Authorization": self.generate_token(self.test_user_payload),
            "Content-Type": "application/json"
        }
        self.success_ops = {
            "Authorization": self.generate_token(self.test_successops_payload),
            "Content-Type": "application/json"
        }
        self.society_president = {
            "Authorization": self.generate_token(
                self.test_society_president_role_payload),
            "Content-Type": "application/json"
        }

        self.society_secretary = {
            "Authorization": self.generate_token(
                                self.test_society_secretary_payload),
            "Content-Type": "application/json"
            }
        self.cio = {
            "Authorization": self.generate_token(
                self.test_cio_role_payload),
            "Content-Type": "application/json"
        }
        self.finance = {
            "Authorization": self.generate_token(
                self.test_finance_payload),
            "Content-Type": "application/json"
        }
        self.bad_token_header = {
            "Authorization": self.generate_token(
                {"I don't know": "what to put here"}
            ),
            "Content-Type": "application/json"
        }

        # test centers
        self.nairobi = Center(name='Nairobi')
        self.kampala = Center(name='Kampala')
        self.lagos = Center(name='Lagos')

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
                                    name="success ops")
        self.fellow_role = Role(uuid="-KXGy1EB1oimjQgFim6C", name="Fellow")
        self.success_role = Role(uuid="-KXGy1EB1oimjQgFim6F",
                                 name="success ops")
        self.finance_role = Role(uuid="-KXGy1EB1oimjQgFim6L", name="finance")
        self.lf_role = Role(uuid="d47ec8a7-3f09-44a5-8188-ff1d40ef35b6",
                            name="Learning Facilitator")
        self.president_role = Role(uuid="-KXGyd2udi2",
                                   name="society president")
        self.v_president_role = Role(uuid="-KXGy32odnd", name="vice president")
        self.secretary_role = Role(uuid="-KXGy12odfn2idn",
                                   name="society secretary")
        self.cio_role = Role(uuid="-KXGionceu24i2y", name="cio")

        # test cohorts
        self.cohort_12_Ke = Cohort(name="cohort-12", center=self.nairobi)
        self.cohort_12_Ug = Cohort(name="cohort-12", center=self.kampala)
        self.cohort_1_Nig = Cohort(name="cohort-1", center=self.lagos)

        # test users
        self.test_user = User(
            uuid="-KdQsMt2U0ixIy_-yWTSZ",
            name="Test User",
            photo="https://www.link.com",
            email="test.user.societies@andela.com",
            center=self.lagos,
            cohort=self.cohort_1_Nig,
            society=self.phoenix
        )
        self.test_user_2 = User(
            uuid="-KdQsawesome_usedk2cckjfbi",
            name="Test User2",
            photo="https://www.link.com",
            email="test.user2.societies@andela.com",
            center=self.kampala,
            cohort=self.cohort_12_Ug,
            society=self.sparks
        )
        self.test_user_3 = User(
            uuid="-KdQsawesomb2dunkdnw",
            name="Test User3",
            photo="https://www.link.com",
            email="test.user3.societies@andela.com",
            center=self.nairobi,
            cohort=self.cohort_12_Ke,
            society=self.invictus
        )

        self.president = User(
            uuid="-KdQsMtixG4U0y_-yJEH",
            name="Test President",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
            email="test.president.societies@andela.com",
            center=self.nairobi,
            cohort=self.cohort_12_Ke,
            society=self.phoenix
        )
        self.president.roles.append(self.president_role)

        self.vice_president = User(
            uuid="-KdQsMtixGc2nuekwnd",
            name="Test Vice-President",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
            email="test.vice_president.societies@andela.com",
            center=self.nairobi,
            cohort=self.cohort_12_Ke,
            society=self.sparks
        )
        self.vice_president.roles.append(self.v_president_role)

        self.secretary = User(
            uuid="-Kuty7hryt8cbkc",
            name="Test Secretary",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
            email="test.secretary.societies@andela.com",
            center=self.nairobi,
            cohort=self.cohort_12_Ke,
            society=self.invictus
        )
        self.secretary.roles.append(self.secretary_role)

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
            value=20,
            supports_multiple_participants=True
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
            name='Bootcamp XIV Interviews - Nairobi',
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

        self.log_alibaba_challenge2 = LoggedActivity(
            name="my second logged activity",
            description="Participated in this event",
            value=2500,
            user=self.test_user,
            activity=self.alibaba_ai_challenge,
            society=self.sparks,
            activity_type=self.hackathon
        )

        self.redemp_req = RedemptionRequest(
            name="T-shirt Funds Request",
            value=2500,
            user=self.test_user,
            center=self.test_user.center,
            society=self.test_user.society
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
        self.patcher.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
