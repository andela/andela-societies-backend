"""Contain utility functions and constants."""
from collections import namedtuple
from flask import current_app, jsonify, request, url_for


PaginatedResult = namedtuple(
    'PaginatedResult',
    ['data', 'count', 'page', 'pages', 'previous_url', 'next_url']
)


def paginate_items(fetched_data, serialize=True):
    """Paginate all roles for display."""
    from api.endpoints.redemption_requests.models import RedemptionRequest
    from api.endpoints.redemption_requests.helpers import serialize_redmp

    _page = request.args.get('page', type=int) or \
        current_app.config['DEFAULT_PAGE']
    _limit = request.args.get('limit', type=int) or \
        current_app.config['PAGE_LIMIT']
    page = current_app.config['DEFAULT_PAGE'] if _page < 0 else _page
    limit = current_app.config['PAGE_LIMIT'] if _limit < 0 else _limit

    fetched_data = fetched_data.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )
    if fetched_data.items:
        previous_url = None
        next_url = None

        if fetched_data.has_next:
            next_url = url_for(request.endpoint, limit=limit,
                               page=page+1, _external=True)
        if fetched_data.has_prev:
            previous_url = url_for(request.endpoint, limit=limit,
                                   page=page-1, _external=True)

        if serialize:
            data_list = []
            for _fetched_item in fetched_data.items:
                if isinstance(_fetched_item, RedemptionRequest):
                    data_item = serialize_redmp(_fetched_item)
                    data_list.append(data_item)
                else:
                    data_item = _fetched_item.serialize()
                    data_list.append(data_item)
        else:
            data_list = fetched_data.items

            return PaginatedResult(
                data_list, fetched_data.total, fetched_data.page,
                fetched_data.pages, previous_url, next_url
            )

        return response_builder(dict(
            status="success",
            data=data_list,
            count=fetched_data.total,
            pages=fetched_data.pages,
            nextUrl=next_url,
            previousUrl=previous_url,
            currentPage=fetched_data.page,
            message="fetched successfully."
        ), 200)

    if not serialize:
        return PaginatedResult(
            [], 0, None, 0, None, None
        )

    return response_builder(dict(
        status="success",
        data=dict(data_list=[],
                  count=0),
        message="Resources were not found."
    ), 404)


def find_item(data):
    """Build the response with found/404 item in DB."""
    # bad design
    # # TODO: Remove local imports from this function, pass model as param
    from api.endpoints.redemption_requests.models import RedemptionRequest
    from api.endpoints.redemption_requests.helpers import serialize_redmp
    if data:

        # Serialization of RedemptionRequest
        if isinstance(data, RedemptionRequest):
            return response_builder(dict(
                data=serialize_redmp(data),
                status="success",
                message="{} fetched successfully.".format(data.name)
            ), 200)

        return response_builder(dict(
            data=data.serialize(),
            status="success",
            message="{} fetched successfully.".format(data.name)
        ), 200)

    return response_builder(dict(
        data=None,
        status="fail",
        message="Resource does not exist."
    ), 404)


def response_builder(data, status_code=200):
    """Build the jsonified response to return."""
    response = jsonify(data)
    response.status_code = status_code
    return response
