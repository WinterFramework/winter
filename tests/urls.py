from http import HTTPStatus

import tests.api
import winter.django
import winter.web
from winter.application import get_injector
from winter.ddd import NotFoundException
from tests.web.interceptors import HelloWorldInterceptor

app = winter.web.WebApplication(modules=[tests.api], injector=get_injector(), interceptors=[HelloWorldInterceptor])
# Mapping a domain exception to an HTTP status is application wiring, not framework behaviour
app.add(winter.web.problem(status=HTTPStatus.NOT_FOUND)(NotFoundException))
urlpatterns = winter.django.create_urls(app)
