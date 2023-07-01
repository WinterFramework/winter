from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthenticationMiddleware
from django.core.handlers.wsgi import WSGIRequest
from .entities import Guest


class AuthenticationMiddleware(DjangoAuthenticationMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self._get_response = get_response

    def __call__(self, request: WSGIRequest):
        if 'ADD_GUEST_USER_TO_REQUEST' in request.META.get('headers', {}):
            request.user = Guest()

        return self._get_response(request)
