import pytest

import winter
from winter.data.pagination import PagePosition
from winter.web.routing import get_route
from winter_openapi import generate_openapi


def test_generate_page_position_argument_spec():
    class _TestAPI:
        @winter.route_get("pageable_resource")
        def method(self, arg1: PagePosition):  # pragma: no cover
            pass

    route = get_route(_TestAPI.method)

    # Act
    result = generate_openapi(title="title", version="1.0.0", routes=[route])

    # Assert
    parameters = result["paths"]["/pageable_resource"]["get"]["parameters"]
    assert parameters == [
        {
            "allowEmptyValue": False,
            "allowReserved": False,
            "deprecated": False,
            "description": "Number of results to return per page",
            "explode": False,
            "in": "query",
            "name": "limit",
            "required": False,
            "schema": {"type": "integer"},
        },
        {
            "allowEmptyValue": False,
            "allowReserved": False,
            "deprecated": False,
            "description": "The initial index from which to return the results",
            "explode": False,
            "in": "query",
            "name": "offset",
            "required": False,
            "schema": {"type": "integer"},
        },
    ]


def test_generate_object_argument_spec():
    class _TestAPI:
        @winter.route_get("pageable_resource")
        def method(self, arg1: object):  # pragma: no cover
            pass

    route = get_route(_TestAPI.method)

    # Act
    result = generate_openapi(title="title", version="1.0.0", routes=[route])

    # Assert
    parameters = result["paths"]["/pageable_resource"]["get"]["parameters"]
    assert parameters == []


@pytest.mark.parametrize("default_sort", (None, ["id"]))
def test_page_position_argument_inspector_with_allowed_order_by_fields(default_sort):
    class TestAPI:
        @winter.route_get("ordered_resource")
        @winter.web.pagination.order_by(["id"], default_sort=default_sort)
        def method(self, arg1: PagePosition):  # pragma: no cover
            pass

    route = get_route(TestAPI.method)
    expected_order_by_parameter = {
        "allowEmptyValue": False,
        "allowReserved": False,
        "deprecated": False,
        "description": "Comma separated order by fields. Allowed fields: id.",
        "explode": False,
        "in": "query",
        "name": "order_by",
        "required": False,
        "schema": {"items": {"type": "string"}, "type": "array"},
    }

    if default_sort:
        expected_order_by_parameter['schema']['default'] = default_sort

    # Act
    result = generate_openapi(title="title", version="1.0.0", routes=[route])

    # Assert
    parameters = result["paths"]["/ordered_resource"]["get"]["parameters"]
    assert parameters == [
        {
            "allowEmptyValue": False,
            "allowReserved": False,
            "deprecated": False,
            "description": "Number of results to return per page",
            "explode": False,
            "in": "query",
            "name": "limit",
            "required": False,
            "schema": {"type": "integer"},
        },
        {
            "allowEmptyValue": False,
            "allowReserved": False,
            "deprecated": False,
            "description": "The initial index from which to return the results",
            "explode": False,
            "in": "query",
            "name": "offset",
            "required": False,
            "schema": {"type": "integer"},
        },
        expected_order_by_parameter
    ]
