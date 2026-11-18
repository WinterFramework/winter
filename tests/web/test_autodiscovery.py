import winter.web
from tests.injection import app_injector
from winter.web.autodiscovery import find_routes


def test_find_routes():
    import tests.api.package

    app = winter.web.WebApplication(modules=[tests.api.package], injector=app_injector)

    # Act
    routes = find_routes(app)

    # Assert
    assert [route.url_path for route in routes] == ['api_1/', 'api_2/', 'api_2/', 'api_3/']
