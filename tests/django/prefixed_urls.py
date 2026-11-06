"""A URLconf with an application under a prefix and a view that Winter does not serve, for tests of route_of."""
from django.http import HttpResponse
from django.urls import path

import winter.django
import winter.web


class OrderAPI:
    @winter.web.route_get('orders/{order_id}/')
    def get(self, order_id: int) -> int:  # pragma: no cover
        return order_id


app = winter.web.WebApplication(modules=[])
app.add(OrderAPI)
urlpatterns = [
    *winter.django.create_urls(app, prefix='api/v1/'),
    path('health/', lambda request: HttpResponse()),
]
