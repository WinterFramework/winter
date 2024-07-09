from django.http import HttpRequest

import winter
from winter.core import ComponentMethod
from winter.web import Interceptor
from winter.web import ResponseHeader


class HelloWorldInterceptor(Interceptor):
    @winter.response_header('x-method', 'method_header')
    @winter.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(
        self,
        method: ComponentMethod,
        request: HttpRequest,
        method_header: ResponseHeader[str],
        hello_world_header: ResponseHeader[str],
    ):
        method_header.set(method.full_name)
        if 'hello_world' in request.GET:
            hello_world_header.set('Hello, World!')
