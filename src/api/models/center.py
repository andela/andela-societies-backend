from api.models.base import Base


db = Base.db


class Center(Base):
    """Models different centres in Andela."""

    __tablename__ = 'centers'

    cohorts = db.relationship('Cohort',
                              back_populates='center',
                              lazy='dynamic',
                              cascade="all, delete, delete-orphan")
    members = db.relationship('User',
                              back_populates='center',
                              lazy='dynamic',
                              cascade="all, delete, delete-orphan")
    redemption_requests = db.relationship(
        'RedemptionRequest',
        back_populates='center',
        lazy='dynamic',
        order_by='desc(RedemptionRequest.created_at)'
    )
