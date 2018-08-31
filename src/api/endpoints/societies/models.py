from api.models import db, Base


class Society(Base):
    """Model Societies in Andela."""

    __tablename__ = 'societies'
    name = db.Column(db.String, nullable=False, unique=True)
    color_scheme = db.Column(db.String)
    logo = db.Column(db.String)
    _total_points = db.Column(db.Integer, default=0)
    _used_points = db.Column(db.Integer, default=0)

    members = db.relationship('User', back_populates='society', lazy='dynamic')
    logged_activities = db.relationship(
        'LoggedActivity', back_populates='society', lazy='dynamic'
    )
    cohorts = db.relationship(
        'Cohort', back_populates='society', lazy='dynamic'
    )
    redemptions = db.relationship(
        'RedemptionRequest', back_populates='society', lazy='dynamic'
    )

    @property
    def total_points(self):
        """Keep track of all society points."""
        return self._total_points

    @total_points.setter
    def total_points(self, point):
        self._total_points += point.value

    @property
    def used_points(self):
        """Keep track of redeemed points."""
        return self._used_points

    @used_points.setter
    def used_points(self, redemption_request):
        self._used_points += redemption_request.value

    @property
    def remaining_points(self):
        """Keep track of points available for redeemption."""
        return self.total_points - self.used_points
