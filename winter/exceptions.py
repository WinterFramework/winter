from rest_framework import status as http_status
from rest_framework.response import Response as HTTPResponse


class WinterException(Exception):
    pass


class RedirectException(WinterException):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to


def handle_winter_exception(exception: WinterException) -> HTTPResponse:
    if isinstance(exception, RedirectException):
        return HTTPResponse(status=http_status.HTTP_302_FOUND, headers={
            'Location': exception.redirect_to,
        })
    raise exception
