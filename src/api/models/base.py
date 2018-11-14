"""Contain All App Models."""
import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError


db = SQLAlchemy()

def generate_uuid():
    """Generate unique string."""
    return str(uuid.uuid1())


def camel_case(snake_str):
    """Convert string to camel case."""
    title_str = snake_str.title().replace("_", "")

    return title_str[0].lower() + title_str[1:]


# many to many relationship between users and activities
user_activity = db.Table('user_activity',
                         db.Column('user_uuid', db.String,
                                   db.ForeignKey('users.uuid'), nullable=False
                                   ),
                         db.Column('activity_uuid', db.String,
                                   db.ForeignKey('activities.uuid'),
                                   nullable=False))
user_role = db.Table('user_role',
                     db.Column('user_uuid', db.String,
                               db.ForeignKey('users.uuid'), nullable=False
                               ),
                     db.Column('role_uuid', db.String,
                               db.ForeignKey('roles.uuid'),
                               nullable=False))


class Base(db.Model):
    """Base model, contain utility methods and properties."""

    db = db

    __abstract__ = True
    uuid = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String)
    photo = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    description = db.Column(db.String)

    def __repr__(self):
        """Repl rep of models."""
        return f"{type(self).__name__}(id='{self.uuid}', name='{self.name}')"

    def __str__(self):
        """Return string representation."""
        return self.name

    def save(self):
        """Save the object in DB.

        Return:
            saved(boolean) true if saved, false otherwise
        """
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def delete(self):
        """Delete the object in DB.

        Return
            deleted(boolean) True if deleted else false
        """
        deleted = None
        try:
            db.session.delete(self)
            db.session.commit()
            deleted = True
        except Exception:
            deleted = False
            db.session.rollback()
        return deleted

    def serialize(self):
        """Map model to a dictionary representation.

        Return:
            A dict object
        """
        dictionary_mapping = {
            camel_case(attribute.name): str(getattr(self, attribute.name))
            if not isinstance(getattr(self, attribute.name), int)
            else getattr(self, attribute.name)
            for attribute in self.__table__.columns
        }
        return dictionary_mapping
