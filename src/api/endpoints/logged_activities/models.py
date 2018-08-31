from api.models import Base

db = Base.db


class LoggedActivity(Base):
    """Models Activities logged by fellows."""

    __tablename__ = 'logged_activities'
    value = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default='in review')
    approved_at = db.Column(db.DateTime)
    activity_date = db.Column(db.Date)
    redeemed = db.Column(db.Boolean, nullable=False, default=False)
    no_of_participants = db.Column(db.Integer)

    approver_id = db.Column(db.String)
    reviewer_id = db.Column(db.String)
    activity_type_id = db.Column(
        db.String, db.ForeignKey('activity_types.uuid'), nullable=False
    )
    user_id = db.Column(db.String, db.ForeignKey('users.uuid'), nullable=False)
    society_id = db.Column(
        db.String, db.ForeignKey('societies.uuid'), nullable=False,
    )
    activity_id = db.Column(db.String, db.ForeignKey('activities.uuid'))

    activity = db.relationship(
        'Activity', back_populates='logged_activities'
    )
    activity_type = db.relationship(
        'ActivityType', back_populates='logged_activities'
    )
    user = db.relationship(
        'User', back_populates='logged_activities'
    )
    society = db.relationship(
        'Society', back_populates='logged_activities'
    )
