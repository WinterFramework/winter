from winter.web.autodiscovery import find_package_routes


def test_find_package_routes():
    # Act
    routes = find_package_routes('tests.api.package')

    # Assert
    assert [route.url_path for route in routes] == ['api_1/', 'api_2/', 'api_2/', 'api_3/']
