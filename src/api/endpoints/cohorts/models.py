from api.models.base import Base


db = Base.db


class Cohort(Base):
    """Models cohorts available in Andela."""

    __tablename__ = 'cohorts'
    center_id = db.Column(db.String, db.ForeignKey('centers.uuid'),
                          nullable=False)
    society_id = db.Column(db.String, db.ForeignKey('societies.uuid'))

    center = db.relationship('Center', back_populates='cohorts')
    society = db.relationship('Society', back_populates='cohorts')
    members = db.relationship('User', back_populates='cohort', lazy='dynamic')
