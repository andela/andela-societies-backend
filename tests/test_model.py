"""Models TestSuite."""

from api.models import (Activity, ActivityType, Cohort, Country,
                        LoggedActivity, Society, User, Role)
from tests.base_test import BaseTestCase


class UserTestCase(BaseTestCase):
    """Test models."""

    def test_create_user(self):
        """Test we can create user objects."""
        test_user = User(
            uuid="-KdQsMt2U0ixIy_-yJEH",
            name="Larry Wachira",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
            email="lawrence.wachira@andela.com",
            country=self.kenya,
            cohort=self.cohort_12_Ke)

        self.assertTrue(test_user.save())

    def test_get_user(self):
        self.test_user.save()

        user = User.query.filter_by(uuid="-KdQsMt2U0ixIy_-yWTSZ").first()
        self.assertEqual(self.test_user, user)

    def get_all_users(self):
        test_user = User(
            uuid="-KdQsMt2U0ixIy_-yJEH",
            name="Larry Wachira",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
            email="lawrence.wachira@andela.com",
            country=self.kenya,
            cohort=self.cohort_12_Ke)

        test_user.save()
        self.test_user()

        users = User.query.all()

        self.assertListEqual([test_user, self.test_user], users)

    def test_user_can_log_activity(self):

        self.test_user.logged_activities.append(self.log_alibaba_challenge)
        self.test_user.save()

        user_activity = LoggedActivity.query.filter_by(
                            name="my logged activity").first()
        self.assertTrue(user_activity == self.log_alibaba_challenge)

    def test_user_can_participate_activity(self):
        self.test_user.activities.append(self.js_meet_up)
        self.test_user.save()

        user_activity = Activity.query.filter_by(
                            name='Nairobi Js meetup').first()

        self.assertEqual(self.js_meet_up, user_activity)

    def test_payload_has_null_values(self):
        new_user = User(email=None,
                        name=None,
                        uuid="-Ksomeid")

        self.assertFalse(new_user.save())


class SocietyTestCase(BaseTestCase):
    """Test Society model."""

    def test_create_society(self):
        istelle = Society(name="iStelle")

        self.assertTrue(istelle.save())

    def test_adding_members(self):
        self.istelle.members.append(self.test_user)
        self.istelle.save()

        user = User.query.filter_by(society=self.istelle).first()

        self.assertEqual(user, self.test_user)

    def test_get_all_members(self):
        test_user = User(
            uuid="-KdQsMt2U0ixIy_-yJEH",
            name="Larry Wachira",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
            email="lawrence.wachira@andela.com",
            country=self.kenya,
            cohort=self.cohort_12_Ke)

        self.phoenix.members.extend([test_user, self.test_user])
        self.phoenix.save()

        users = User.query.filter_by(society=self.phoenix).all()
        self.assertListEqual(users, [self.test_user, test_user])

    def test_get_society(self):
        self.phoenix.save()

        society = Society.query.filter_by(name="Phoenix").first()

        self.assertEqual(self.phoenix, society)

    def test_get_all_societies(self):
        self.phoenix.save()
        self.istelle.save()
        self.sparks.save()
        self.invictus.save()

        societies = Society.query.all()

        self.assertListEqual(
            societies,
            [self.phoenix, self.istelle,  self.sparks, self.invictus])

    def test_save_null_values(self):
        """Test for false return if society name is null."""
        test_society = Society(name=None)
        self.assertFalse(test_society.save())

    def test_delete_existing_society(self):
        """Test if society has been deleted successfully."""
        self.invictus.save()
        self.assertTrue(self.invictus.delete())

    def test_delete_nonexistent_society(self):
        """Test for false return if nonexistent society is deleted."""
        test_society = Society(name="Persia")
        self.assertFalse(test_society.delete())


class ActivityTestCase(BaseTestCase):
    """Test Activity model."""

    def test_create_activity(self):
        google_hash_code = Activity(name='Google Tough hackathon',
                                    activity_type=self.hackathon)
        self.assertTrue(google_hash_code.save())

    def test_get_activity(self):
        self.alibaba_ai_challenge.save()

        activity = Activity.query.filter_by(name='Fashion challenge').first()

        self.assertEqual(self.alibaba_ai_challenge, activity)


class ActivityTypeTestCase(BaseTestCase):
    """Test suite for ActivityType model."""

    def test_create_activityType(self):
        hackathon = ActivityType(name="Hackathon",
                                 description="Participating in a Hackathon",
                                 value=100)
        tech_event = ActivityType(name="Tech Event",
                                  description="Organize a tech event",
                                  value=2500)

        self.assertTrue(hackathon.save() and tech_event.save())


class LoggedActivityTestCase(BaseTestCase):
    """Tests suite for LoggedActivity model."""

    def test_create_logged_activity(self):
        log_alibaba_challenge = LoggedActivity(
            name="my logged activity",
            description="Participated in this event",
            value=2500,
            user=self.test_user,
            activity=self.alibaba_ai_challenge,
            society=self.phoenix)

        self.assertTrue(log_alibaba_challenge.save())

    def test_get_user_logged_activity(self):
        self.log_alibaba_challenge.save()

        logged_activity = LoggedActivity.query.filter_by(
                name="my logged activity").first()

        self.assertEqual(logged_activity, self.log_alibaba_challenge)

    def test_get_society_logged_activities(self):
        self.log_alibaba_challenge.save()

        self.assertListEqual(
            self.phoenix.logged_activities, [self.log_alibaba_challenge])


class CohortTestCase(BaseTestCase):
    """Tests suite for Cohort model."""

    def test_create_cohort(self):
        cohort_1_Nig = Cohort(name="cohort-1", country=self.nigeria)
        self.assertTrue(cohort_1_Nig.save())


class CountryTestCase(BaseTestCase):
    """Tests suite for Country model."""

    def test_create_country(self):
        self.uganda = Country(name='Uganda')

        self.assertTrue(self.uganda.save())


class RoleTestCase(BaseTestCase):
    """Test suite for Role Model."""

    def test_create_role(self):
        self.success_ops = Role(uuid="-KkLwgbeJUO0dQKsEk1i",
                                name="Success Ops")

        self.assertTrue(self.success_ops.save())
