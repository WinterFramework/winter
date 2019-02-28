import pytest
from rest_framework.views import APIView

import winter
from winter.http import MediaType
from winter.routing import get_route
from winter.schema.inspectors import SwaggerAutoSchema


@pytest.fixture
def auto_schema():
    view = View()
    View.post.method = Controller.post
    route = get_route(Controller.post)
    try:
        yield SwaggerAutoSchema(view, 'path', route.http_method, 'components', 'request', {})
    finally:
        del View.post.method


def get_empty_swagger_auto_schema(method: str = 'post'):
    view = View()

    return SwaggerAutoSchema(view, 'path', method, 'components', 'request', {})


class View(APIView):

    def post(self):
        return


class Controller:

    @winter.route_post('/', produces=(MediaType.MULTIPART_FORM_DATA,), consumes=(MediaType.APPLICATION_JSON,))
    def post(self):
        pass


def test_get_produces(auto_schema):
    consumes = auto_schema.get_produces()
    assert consumes == [str(MediaType.MULTIPART_FORM_DATA)]


def test_get_consumes(auto_schema):
    consumes = auto_schema.get_consumes()
    assert consumes == [str(MediaType.APPLICATION_JSON)]


def test_get_produces_without_method():
    auto_schema = get_empty_swagger_auto_schema()
    consumes = auto_schema.get_produces()
    assert consumes == ['application/json']


@pytest.mark.parametrize('method', ('post', 'patch'))
def test_get_consumes_without_method(method):
    auto_schema = get_empty_swagger_auto_schema(method)
    consumes = auto_schema.get_consumes()
    assert consumes == ['application/json']
