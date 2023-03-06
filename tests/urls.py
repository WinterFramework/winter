from winter.web import find_package_routes
from winter_django import create_django_urls_from_routes

routes = find_package_routes('tests.api')
urlpatterns = create_django_urls_from_routes(routes)
