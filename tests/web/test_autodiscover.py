from winter.web.autodiscovery import get_routes_by_package


def test_get_routes_by_package():
    # Act
    routes = get_routes_by_package('tests.api.package')

    # Assert
    assert [route.url_path for route in routes] == ['api_1/', 'api_2/', 'api_2/', 'api_3/']
