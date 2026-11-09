import winter.web
from winter.web import Interceptor
from winter.web import Request
from winter.web import ResponseHeader
from winter.web import Route


class HelloWorldInterceptor(Interceptor):
    @winter.web.response_header('x-method', 'method_header')
    @winter.web.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(
        self,
        route: Route,
        request: Request,
        method_header: ResponseHeader[str],
        hello_world_header: ResponseHeader[str],
    ):
        method_header.set(route.method.full_name)
        if 'hello_world' in request.query_parameters:
            hello_world_header.set('Hello, World!')
