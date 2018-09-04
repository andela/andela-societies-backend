from api.models.base import Base


db = Base.db


class User(Base):
    """Models Users."""

    __tablename__ = 'users'

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    society_id = db.Column(db.String, db.ForeignKey('societies.uuid'))
    center_id = db.Column(db.String, db.ForeignKey('centers.uuid'))
    cohort_id = db.Column(db.String, db.ForeignKey('cohorts.uuid'))

    society = db.relationship('Society', back_populates='members')
    cohort = db.relationship('Cohort', back_populates='members')
    center = db.relationship('Center', back_populates='members')
    logged_activities = db.relationship(
        'LoggedActivity',
        back_populates='user',
        lazy='dynamic',
        order_by='desc(LoggedActivity.created_at)'
    )
    created_activities = db.relationship(
        'Activity',
        backref='added_by',
        lazy='dynamic'
    )
    activities = db.relationship(
        'Activity',
        secondary='user_activity',
        lazy='dynamic',
        backref='participants'
    )
    redemption_requests = db.relationship(
        'RedemptionRequest',
        back_populates='user',
        lazy='dynamic',
        order_by='desc(RedemptionRequest.created_at)'
    )
    roles = db.relationship(
        'Role',
        secondary='user_role',
        back_populates='users',
        lazy='dynamic'
    )
