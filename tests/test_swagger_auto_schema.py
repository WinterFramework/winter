import winter
from winter.http import MediaType
from winter.routing import get_route
from winter.schema.inspectors import SwaggerAutoSchema


def get_swagger_auto_schema():
    controller = Controller()
    route = get_route(Controller.post)
    return SwaggerAutoSchema(controller, 'path', route.http_method, 'components', 'request', {})


def get_empty_swagger_auto_schema():
    controller = Controller()
    return SwaggerAutoSchema(controller, 'path', 'patch', 'components', 'request', {})


class Controller:

    @winter.route_post('/', produces=(MediaType.MULTIPART_FORM_DATA,), consumes=(MediaType.APPLICATION_JSON,))
    def post(self):
        pass


def test_get_produces():
    auto_schema = get_swagger_auto_schema()
    consumes = auto_schema.get_produces()
    assert consumes == [str(MediaType.MULTIPART_FORM_DATA)]


def test_get_consumes():
    auto_schema = get_swagger_auto_schema()
    consumes = auto_schema.get_consumes()
    assert consumes == [str(MediaType.APPLICATION_JSON)]


def test_get_produces_without_method():
    auto_schema = get_empty_swagger_auto_schema()
    consumes = auto_schema.get_produces()
    assert consumes == []


def test_get_consumes_without_method():
    auto_schema = get_empty_swagger_auto_schema()
    consumes = auto_schema.get_consumes()
    assert consumes == []