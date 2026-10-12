from collections.abc import Mapping

import django.http

from winter.web import Request


class DjangoRequest(Request):
    """winter.web.Request on top of a Django HttpRequest."""

    def __init__(self, django_request: django.http.HttpRequest, path_parameters: Mapping[str, str]):
        self.django_request = django_request
        self._path_parameters = path_parameters

    @property
    def method(self) -> str:
        return self.django_request.method

    @property
    def path(self) -> str:
        return self.django_request.path

    @property
    def full_path(self) -> str:
        return self.django_request.get_full_path()

    @property
    def query_parameters(self) -> django.http.QueryDict:
        return self.django_request.GET

    @property
    def headers(self) -> Mapping[str, str]:
        return self.django_request.headers

    @property
    def path_parameters(self) -> Mapping[str, str]:
        return self._path_parameters

    @property
    def body(self) -> bytes:
        return self.django_request.body

    @property
    def remote_address(self) -> str | None:
        return self.django_request.META.get('REMOTE_ADDR')
