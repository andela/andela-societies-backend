from api.models import Base

db = Base.db


class ActivityType(Base):
    """Models activity types."""

    __tablename__ = 'activity_types'

    value = db.Column(db.Integer, nullable=False)
    supports_multiple_participants = db.Column(db.Boolean, default=False)

    activities = db.relationship(
        'Activity',
        back_populates='activity_type',
        lazy='dynamic'
    )
    logged_activities = db.relationship(
        'LoggedActivity',
        back_populates='activity_type',
        lazy='dynamic',
        order_by='desc(LoggedActivity.created_at)'
    )
