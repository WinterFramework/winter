import winter.web


def test_find_package_routes():
    # Act
    routes = winter.web.find_package_routes('tests.api.package')

    # Assert
    assert [route.url_path for route in routes] == ['api_1/', 'api_2/', 'api_2/', 'api_3/']


def test_find_module_routes():
    # Act
    routes = winter.web.find_package_routes('tests.api.package.api_2')

    # Assert
    assert [route.url_path for route in routes] == ['api_2/', 'api_2/']
