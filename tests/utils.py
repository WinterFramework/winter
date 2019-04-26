from django.http import HttpRequest
from django.http import QueryDict
from rest_framework.request import Request


def get_request(query_string=''):
    django_request = HttpRequest()
    django_request.GET = QueryDict(query_string, mutable=True)
    return Request(django_request)
