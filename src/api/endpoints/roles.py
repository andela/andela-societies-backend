"""Role Module."""

from flask import jsonify, request, current_app, url_for
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.utils.marshmallow_schemas import role_schema
from ..models import Role


class RoleAPI(Resource):
    """To contain CRUD endpoints for Role."""

    @token_required
    @roles_required(["Success Ops"])
    def post(self):
        """Create a role."""
        payload = request.get_json()

        result, errors = role_schema.load(payload)

        if errors:
            response = jsonify(errors)
            status_code = role_schema.context.get('status_code')
            role_schema.context = {}
            response.status_code = status_code or 400
        else:
            role = Role(name=result['name'])
            role.save()

            response = jsonify({'message': 'Role created successfully.',
                                'data': result})
            response.status_code = 201

        return response

    @token_required
    def get(self, role_id=None):
        """Get Role(s) details."""
        if role_id:
            role = Role.query.get(role_id)
            if role:
                response = jsonify({
                    "data": role.serialize(),
                    "status": "success",
                    "message": "Role {} fetched successfully.".format(role.name)
                })
                response.status_code = 200
                # return response
            else:
                response = jsonify({
                    "data": None,
                    "status": "fail",
                    "message": "Specified role does not exist."
                })
                response.status_code = 404
            return response
        else:
            _page = request.args.get('page')
            _limit = request.args.get('limit')
            page = int(_page or current_app.config['DEFAULT_PAGE'])
            limit = int(_limit or current_app.config['PAGE_LIMIT'])
            roles = Role.query

            roles = roles.paginate(
                page=page,
                per_page=limit,
                error_out=False
            )
            if roles.items:
                previous_url = None
                next_url = None
                if roles.has_next:
                    next_url = url_for(request.endpoint, limit=limit,
                                       page=page+1, _external=True)
                if roles.has_prev:
                    previous_url = url_for(request.endpoint, limit=limit,
                                           page=page-1, _external=True)

                roles_list = []
                for _role in roles.items:
                    role = _role.serialize()
                    roles_list.append(role)

                response = jsonify({
                    "status": "success",
                    "data": {"roles": roles_list,
                             "count": len(roles.items),
                             "nextUrl": next_url,
                             "previousUrl": previous_url,
                             "currentPage": roles.page},
                    "message": "Role fetched successfully."
                })
                response.status_code = 200
                return response
            else:
                response = jsonify({
                    "status": "success",
                    "data": {"roles": [],
                             "count": 0},
                    "message": "There are no roles."
                })
                response.status_code = 404
                return response

    @token_required
    @roles_required(["Success Ops"])
    def put(self, role_id):
        """Edit Role details."""
        payload = request.get_json()

        if payload:
            if not role_id:
                # if role_id is not passed
                return {"status": "fail",
                        "message": "Role id must be provided."}, 400

            role = Role.query.get(role_id)
            if role:
                name = payload["name"]
                color_scheme = payload["colorScheme"]
                logo = payload["logo"] or None
                photo = payload["photo"]or None
                if name:
                    role.name = name
                if color_scheme:
                    role.color = color_scheme
                if photo:
                    role.photo = logo
                if logo:
                    role.logo = photo
                role.save()
                response = jsonify({
                    "data": {"path": role.serialize()},
                    "status": "success"
                })
            else:
                response = jsonify({"status": "fail",
                                    "message": "Role does not exist."})
                response.status_code = 404
            return response

    @token_required
    @roles_required(["Success Ops"])
    def delete(self, role_id):
        """Delete a role."""
        if not role_id:
            return {"status": "fail",
                    "message": "Role id must be provided."}, 400
        role = Role.query.get(role_id)
        if not role:
            response = jsonify({"status": "fail",
                                "message": "Role does not exist."})
            response.status_code = 404
            return response
        else:
            role.delete()
            response = jsonify({"status": "success",
                                "message": "Role deleted successfully."})
            response.status_code = 200
            return response
