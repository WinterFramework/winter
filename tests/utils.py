from django.http import HttpRequest
from django.http import QueryDict

from winter.django import DjangoRequest


def get_request(query_string='', path_parameters=None) -> DjangoRequest:
    django_request = HttpRequest()
    django_request.GET = QueryDict(query_string, mutable=True)
    return DjangoRequest(django_request, path_parameters or {})
