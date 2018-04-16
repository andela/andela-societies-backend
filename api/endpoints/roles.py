"""Module for Roles in Andela."""
from flask import jsonify, request, current_app, url_for
from flask_restplus import Resource


from api.utils.auth import (token_required, roles_required)
from api.models import Role


class RoleAPI(Resource):
    """Role Resource to contain CRUD endpoints for roles."""

    @token_required
    @roles_required(["Success Ops"])
    def get(self, role_id=None):
        """Retrieve Roles within the API."""
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
                    "message": "Roles fetched successfully."
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
