from api.models.base import Base


db = Base.db


class Activity(Base):
    """Model activities available for points."""

    __tablename__ = 'activities'

    activity_type_id = db.Column(
        db.String,
        db.ForeignKey('activity_types.uuid'),
        nullable=False
    )
    added_by_id = db.Column(
        db.String,
        db.ForeignKey('users.uuid'),
        nullable=False
    )

    activity_date = db.Column(db.Date)

    logged_activities = db.relationship(
        'LoggedActivity',
        back_populates='activity',
        lazy='dynamic',
        order_by='desc(LoggedActivity.created_at)'
    )
    activity_type = db.relationship(
        'ActivityType',
        back_populates='activities',
        uselist=False
    )
