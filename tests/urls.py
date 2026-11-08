from http import HTTPStatus

import tests.api
import winter.ddd.exceptions
import winter.django
import winter.web
from tests.injection import app_injector
from winter.ddd import NotFoundException
from tests.web.interceptors import HelloWorldInterceptor

# Mapping a domain exception to an HTTP status is application wiring, not framework behaviour
winter.web.problem(status=HTTPStatus.NOT_FOUND)(NotFoundException)
app = winter.web.WebApplication(
    modules=[tests.api, winter.ddd.exceptions],
    injector=app_injector,
    interceptors=[HelloWorldInterceptor],
)
urlpatterns = winter.django.create_urls(app)
