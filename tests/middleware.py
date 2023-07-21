from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthenticationMiddleware
from django.core.handlers.wsgi import WSGIRequest

from .entities import AuthorizedUser
from .entities import Guest


class AuthenticationMiddleware(DjangoAuthenticationMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self._get_response = get_response
        self._guest = Guest()
        self._user = AuthorizedUser()

    def __call__(self, request: WSGIRequest):
        authorize_as = request.META.get('HTTP_TEST_AUTHORIZE', '').lower()
        if authorize_as == 'guest':
            request.user = self._guest
        elif authorize_as == 'user':
            request.user = self._user

        return self._get_response(request)
