from django.http import HttpRequest
from django.http import QueryDict


def get_request(query_string=''):
    django_request = HttpRequest()
    django_request.GET = QueryDict(query_string, mutable=True)
    return django_request
