import dataclasses

import winter
from winter.pagination import Page
from winter.pagination import PagePosition


@winter.controller
@winter.route('winter_no_auth')
@winter.no_authentication
class NoAuthenticationController:

    @winter.route_get('/')
    @winter.query_parameter('name')
    def hello(self) -> str:
        return f'Hello, World!'
