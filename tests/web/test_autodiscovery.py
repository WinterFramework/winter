from winter.application import Application
from winter.application import get_injector
from winter.web.autodiscovery import find_routes


def test_find_routes():
    import tests.api.package

    app = Application(modules=[tests.api.package], injector=get_injector())

    # Act
    routes = find_routes(app)

    # Assert
    assert [route.url_path for route in routes] == ['api_1/', 'api_2/', 'api_2/', 'api_3/']
