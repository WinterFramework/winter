from winter.web import find_package_routes
from winter_django import create_django_urls_from_routes

routes = find_package_routes('tests.api')
tests_api_urls = create_django_urls_from_routes(routes)

messaging_routes = find_package_routes('tests.winter_messaging.app_sample')
tests_messaging_urls = create_django_urls_from_routes(messaging_routes)

urlpatterns = tests_api_urls + tests_messaging_urls
