from api.models.base import Base


db = Base.db


class RedemptionRequest(Base):
    """Model all redemption requests by Society Presidents."""

    __tablename__ = 'redemptions'

    user_id = db.Column(
        db.String, db.ForeignKey('users.uuid'),
        nullable=False
    )
    society_id = db.Column(
        db.String, db.ForeignKey('societies.uuid'),
        nullable=False
    )
    center_id = db.Column(
        db.String, db.ForeignKey('centers.uuid'),
        nullable=False
    )

    value = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="pending", nullable=False)
    comment = db.Column(db.String)
    rejection = db.Column(db.String)

    user = db.relationship(
        'User',
        back_populates='redemption_requests'
    )
    society = db.relationship(
        'Society',
        back_populates='redemptions'
    )
    center = db.relationship(
        'Center',
        back_populates='redemption_requests'
    )
