"""Test suite for Point Redemption Module."""

from .base_test import BaseTestCase, User


class PointRedemptionBaseTestCase(BaseTestCase):
    """Test class for Society point redemption including endpoint."""

    def setUp(self):
        """Set up all needed variables."""
        BaseTestCase.setUp(self)
        self.president_role.save()
        self.v_president_role.save()
        self.successops_role.save()
        self.invictus.save()
        self.istelle.save()
        self.sparks.save()
        self.phoenix.save()
        self.redemp_req.save()
        self.test_cio.save()

        self.sparks_president = User(
            uuid="-KdQsMtixG4U0y_-yJEHsparks",
            name="Test Sparks President",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAnAABc/ImeP_cAI/photo.jpg?sz=50",
            email="test.sparks.president.societies@andela.com",
            center=self.nairobi,
            cohort=self.cohort_12_Ke,
            society=self.sparks
        )
        self.sparks_president.roles.append(self.president_role)
