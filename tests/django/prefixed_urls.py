"""A URLconf with an application under a prefix and a view that Winter does not serve, for tests of route_of."""
from django.http import HttpResponse
from django.urls import path

import winter.django
import winter.web
from tests.web_application import web_application


class OrderAPI:
    @winter.web.route_get('orders/{order_id}/')
    def get(self, order_id: int) -> int:  # pragma: no cover
        return order_id


urlpatterns = [
    *winter.django.create_urls(web_application(OrderAPI), prefix='api/v1/'),
    path('health/', lambda request: HttpResponse()),
]
