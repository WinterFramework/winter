from winter_django import create_django_urls_for_package


def test_create_django_urls_for_package():
    uripatterns = create_django_urls_for_package('tests.controllers.package')
    assert len(uripatterns) == 3
