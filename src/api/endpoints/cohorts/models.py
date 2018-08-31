from api.models import db, Base


class Cohort(Base):
    """Models cohorts available in Andela."""

    __tablename__ = 'cohorts'
    center_id = db.Column(db.String, db.ForeignKey('centers.uuid'),
                          nullable=False)
    society_id = db.Column(db.String, db.ForeignKey('societies.uuid'))

    society = db.relationship('Society', back_populates='cohorts')
    members = db.relationship('User', back_populates='cohort', lazy='dynamic')
