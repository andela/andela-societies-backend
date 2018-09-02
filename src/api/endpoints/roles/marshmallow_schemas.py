from marshmallow import ValidationError, post_load

from api.utils.marshmallow_schemas import BaseSchema

from .models import Role


class RoleSchema(BaseSchema):
    """Create a validation schema for Roles."""

    @post_load
    def verify_role(self, data):
        """Extra validation of roles."""
        existing_role = Role.query.filter(
            Role.name.ilike(data['name'])).first()

        if existing_role:
            self.context = {'status_code': 409}
            raise ValidationError({'message': 'Role already exists!'})


role_schema = RoleSchema()
