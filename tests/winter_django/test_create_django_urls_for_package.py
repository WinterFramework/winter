from winter_django.autodiscovery import create_django_urls_for_package


def test_create_django_urls_for_package():
    uripatterns = create_django_urls_for_package('tests.api.package')
    assert len(uripatterns) == 4
