from api.models.base import Base


db = Base.db


class Role(Base):
    """Models Roles to which all Andelans have."""

    __tablename__ = 'roles'

    users = db.relationship(
        'User',
        secondary='user_role',
        lazy='dynamic',
        back_populates='roles'
    )
