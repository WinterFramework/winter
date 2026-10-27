# Winter

[![Build Status](https://github.com/WinterFramework/winter/workflows/Testing/badge.svg?branch=master)](https://github.com/WinterFramework/winter/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/876abe42ca943d9c6014/maintainability)](https://codeclimate.com/github/WinterFramework/winter/maintainability)
[![PyPI version](https://badge.fury.io/py/winter.svg)](https://badge.fury.io/py/winter)
[![Gitter](https://badges.gitter.im/winter-python/community.svg)](https://gitter.im/winter-python/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Web Framework with focus on python typing, dataclasses and modular design

# Main features
* Declarative API
* Built around python type annotations
* Dataclasses can be used as request and response body
* Automatic request validation based on types
* Automatic OpenAPI (swagger) documentation generation
* Dependency injection
* Exception handling without boilerplate in accordance with [RFC 7807](https://tools.ietf.org/html/rfc7807)

# Architecture

Package structure and layer rules: [docs/architecture.md](docs/architecture.md).

## Upgrading to Winter 34

A web application is composed explicitly in a `winter.web.WebApplication`, which imports every module of the
given packages and their subpackages on construction, and adapters build from it. `find_package_routes`,
`create_django_urls_from_routes`, `WinterApplication` and the `setup()` functions of `winter.web`, `winter.django`
and `winter.openapi` are gone.

```python
import service_a
import winter.django
import winter.web

app = winter.web.WebApplication(modules=[service_a], injector=injector)  # applications may share one injector
urlpatterns = winter.django.create_urls(app)
```

- An exception handler is a method marked with `@winter.web.exception_handler` whose first argument is
  annotated with the exceptions it handles; the class is created by the injector. `ExceptionHandler`,
  `exception_handlers_registry` with `add_handler` and `set_default_handler`, and the handler argument of
  `@raises` are gone: `@raises(Exc)` only declares the response for OpenAPI.

  ```python
  class FileStorageExceptionHandlers:
      @winter.web.exception_handler
      @winter.web.response_status(HTTPStatus.BAD_GATEWAY)
      def handle_download(self, exception: FileStorageDownloadException) -> ErrorDTO:
          ...
  ```

- Exception handlers belong to applications: a handler, like a `@problem` exception, handles exceptions in the
  applications whose definitions include it, in every endpoint, whether declared with `@raises` or not. Define it
  in a scanned module or add it, e.g. `app.add(winter.web.problem(status=404)(NotFoundException))`.
  The handler of the nearest class in the exception's MRO handles it; two handlers of one exception class in an
  application fail on startup. A handler of the application replaces the built-in handler of the same exception
  class: a handler of `Exception` replaces the default 500 response.
- Arguments come from the request or from the injector of the application, see
  [Values from the injector](#values-from-the-injector). Custom argument resolvers are gone: `ArgumentResolver`,
  `ArgumentsResolver`, `arguments_resolver`, `RequestBodyArgumentResolver`, `ResponseHeaderArgumentResolver`,
  `winter.web.pagination.PagePositionArgumentResolver` and `winter.django.HttpRequestArgumentResolver`. A resolver
  of a type becomes a provider of that type marked `@winter.web.request_scope`. An argument of an API method, an
  interceptor or an exception handler that is neither mapped from the request nor bound in the injector fails on
  startup instead of on the first request.
- An argument named `response_headers` of an exception handler no longer receives the headers of the response:
  declare a `ResponseHeader[T]` with `@winter.web.response_header`, as in an API method.
- A response header is a `str`, an `int` or a `datetime`, the types HTTP has a format for: `ResponseHeader[T]` of
  another type fails with `TypeError` on import, so a UUID or an enum is set as a `str` (`str(uid)`, `status.value`).
  `set` checks the value against `T`. A `datetime` goes as an HTTP-date in GMT in every header, not as ISO 8601, and
  needs a time zone. `response_headers_serializer` and `ResponseHeaderSerializer` are gone.
- Interceptors belong to applications: `WebApplication(..., interceptors=[AuthorizationInterceptor, AuditInterceptor])`
  lists their classes in the order they run. The injector of each request creates them, so their dependencies go
  to `__init__`. `interceptor_registry` and `InterceptorRegistry` are gone.
- Output processors are gone: `register_output_processor_resolver`, `IOutputProcessor`, `IOutputProcessorResolver`,
  `register_output_processor` and `winter.django.output_template`. An API method returns data, encoded as JSON
  (`winter.json.register_encoder` adds the encoder of a type), or a `winter.web.Response`, e.g. a rendered template:
  `Response(HTTPStatus.OK, render_to_string('report.html', context).encode(), {'content-type': 'text/html'})`.
- The `meta` of a `Page` has no `previous` and `next` links any more, and `winter.web.pagination.utils` with
  `get_previous_page_url` and `get_next_page_url` is gone.
- The request pipeline takes the injector from the application. `winter.application.set_injector` is needed only
  by `winter.sqlalchemy`, `winter.ddd` and `winter.messaging`.
- Throttling counts in the storage that the injector of the application binds,
  e.g. `binder.bind(ThrottlingStorage, to=RedisThrottlingStorage(configuration))`; an application with `@throttling`
  and no storage fails on startup. The Django adapter throttles by the Django user, by the client address otherwise.
  `set_throttling_storage` and `set_throttling_identity_resolver` are gone.
- `winter.web.throttling.reset(request, scope)` is gone: an API method with `@throttling` declares a
  `throttle: winter.web.Throttle` argument, and `throttle.reset()` forgets what the scope has counted for the sender:
  for the identity that the request was counted for, even if the method has logged the user in since.
- `register_native_response_type` is gone: an adapter passes the response types of its framework to `handle_request`.
  An API method may still return a Django response.
- OpenAPI: `generate_openapi(app, title=..., version=...)` returns the spec and checks `@raises` annotations
  of the application (`allow_missing_raises_annotation=True` skips the check).
  `winter.openapi.serve_spec(app, spec, url='openapi.json')` and
  `winter.openapi.serve_swagger_ui(app, spec_url='openapi.json', url='docs/')` add the routes that serve them;
  the served spec and Swagger UI work under whatever prefix the application is included at.

## Upgrading to Winter 33

`winter` is a namespace package now: the `import winter` facade is gone, use `winter.web` instead
(`@winter.web.route_get(...)`). `winter_openapi`, `winter_django`, `winter_sqlalchemy`, `winter_ddd`,
`winter.core` and `winter.data` are gone; their contents live under `winter.<package>` as described in
[docs/architecture.md](docs/architecture.md). A codemod rewrites a code base, preserving formatting:

```
pip install libcst
python tools/migrate_to_33.py path/to/your/project
```

`winter.web` does not depend on Django any more. What the codemod cannot do for you:

- Custom `ArgumentResolver`, `IOutputProcessor`, `ExceptionMapper` and `Interceptor` implementations receive
  `winter.web.Request` instead of `django.http.HttpRequest`: `request.query_parameters`, `request.headers`,
  `request.body`, `request.path_parameters`, `request.full_path`. API methods that declare a `HttpRequest`
  argument still get the Django request. `winter.web.throttling.reset`, `get_next_page_url` and
  `get_previous_page_url` from `winter.web.pagination.utils` take a `winter.web.Request` too.
- Raw responses: return `winter.web.Response(status_code, body=bytes, headers={...})`; returning a Django
  `HttpResponse` still works under the Django adapter.
- `winter.ddd.NotFoundException` is not mapped to HTTP 404 by the framework. Add
  `winter.web.problem(status=404)(NotFoundException)` before `winter.web.setup()`.
- Throttling storage is explicit: `winter.web.set_throttling_storage(RedisThrottlingStorage(configuration))`
  from `winter.redis.throttling`, or `InMemoryThrottlingStorage()` for a single process.
- `Request` has no `user`. Who gets throttled is decided by the identity resolver: `winter.django.setup()`
  installs one that uses the Django user, `winter.web.set_throttling_identity_resolver` replaces it.

# How to use

Check out [Getting Started](https://github.com/WinterFramework/winter-getting-started) project for more information

## Installation
```
pip install winter
```

## Hello world
```python
import winter.web

class HelloWorld:
    @winter.web.route_get('/hello/')
    def hello(self) -> str:
        return 'Hello, world!'
```

To use it with Django, in `urls.py`:
```python
import some_package
import winter.django
import winter.web

app = winter.web.WebApplication(modules=[some_package])
urlpatterns = [
    *winter.django.create_urls(app),
]
```

## Todo list CRUD example:
```python
from http import HTTPStatus
from typing import List
from typing import Optional

import winter.web
import winter.web
from dataclasses import dataclass
from winter.pagination import Page
from winter.pagination import PagePosition


@dataclass
class NewTodoDTO:
    todo: str


@dataclass
class TodoUpdateDTO:
    todo: str


@dataclass
class TodoDTO:
    todo_index: int
    todo: str


@winter.web.problem(status=HTTPStatus.NOT_FOUND)
class NotFoundException(Exception):
    def __init__(self, todo_index: int):
        self.index = todo_index


todo_list: List[str] = []


@winter.web.route('todo/')
class TodoAPI:
    @winter.web.route_post('')
    @winter.web.request_body(argument_name='new_todo_dto')
    def create_todo(self, new_todo_dto: NewTodoDTO) -> TodoDTO:
        todo_list.append(new_todo_dto.todo)
        return self._build_todo_dto(len(todo_list) - 1)

    @winter.web.route_get('{todo_index}/')
    def get_todo(self, todo_index: int) -> TodoDTO:
        self._check_index(todo_index)
        return self._build_todo_dto(todo_index)

    @winter.web.route_get('{?q}')
    def get_todo_list(self, page_position: PagePosition, q: Optional[str] = None) -> Page[TodoDTO]:
        q = q if q is None else q.lower()
        dto_list = [
            TodoDTO(todo_index=todo_index, todo=todo)
            for todo_index, todo in enumerate(todo_list)
            if q is None or q in todo.lower()
        ]
        limit = page_position.limit
        offset = page_position.offset
        paginated_dto_list = dto_list[offset: offset + limit]
        return Page(total_count=len(dto_list), items=paginated_dto_list, position=page_position)

    @winter.web.route_get('{todo_index}/')
    @winter.web.request_body(argument_name='todo_update_dto')
    def update_todo(self, todo_index: int, todo_update_dto: TodoUpdateDTO):
        self._check_index(todo_index)
        todo_list[todo_index] = todo_update_dto.todo

    @winter.web.route_get('{todo_index}/')
    def delete_todo(self, todo_index: int):
        self._check_index(todo_index)
        del todo_list[todo_index]

    def _check_index(self, todo_index: int):
        if todo_index < 0 or todo_index >= len(todo_list):
            raise NotFoundException(todo_index=todo_index)

    def _build_todo_dto(self, todo_index: int):
        return TodoDTO(todo_index=todo_index, todo=todo_list[todo_index])
```


## Extending Page class
```python
import winter.web
import winter.web
from dataclasses import dataclass
from winter.pagination import Page
from winter.pagination import PagePosition
from typing import TypeVar
from typing import Generic


T = TypeVar('T')

@dataclass(frozen=True)
class CustomPage(Page, Generic[T]):
    extra_field: str  # The field will go to meta JSON response field


class Example:
    @winter.web.route_get('/')
    def create_todo(self, page_position: PagePosition) -> CustomPage[int]:
        return CustomPage(
            # Standard Page fields
            total_count=3,
            items=[1, 2, 3],
            position=page_position,
            # Custom fields
            extra_field=456,
        )
```


## Exception handling
```python
from dataclasses import dataclass
from http import HTTPStatus
from typing import List

import winter.web


# Minimalist approach. Pointed status and that this exception will be handling automatically. Expected output below:
# {'status': 404, 'type': 'urn:problem-type:todo-not-found', 'title': 'Todo not found', 'detail': 'Incorrect index: 1'}
@winter.web.problem(status=HTTPStatus.NOT_FOUND)
class TodoNotFoundException(Exception):
    def __init__(self, invalid_index: int):
        self.invalid_index = invalid_index

    def __str__(self):
        return f'Incorrect index: {self.invalid_index}'

# Extending output using dataclass. Dataclass fields will be added to response body. Expected output below:
# {'status': 404, 'type': 'urn:problem-type:todo-not-found', 'title': 'Todo not found', 'detail': '', 'invalid_index': 1}
@winter.web.problem(status=HTTPStatus.NOT_FOUND)
@dataclass
class TodoNotFoundException(Exception):
    invalid_index: int

# When we want to build the response body ourselves. Expected output below:
# {'index': 1, 'message': 'Access denied'}
class TodoAccessDeniedException(Exception):
    def __init__(self, index: int):
        self.index = index


@dataclass
class ErrorDTO:
    index: int
    message: str


class TodoExceptionHandlers:
    # Handles the exception its first argument is annotated with, and its subclasses, everywhere in the
    # application. The class is created by the injector. A handler of Exception replaces the default 500 response.
    @winter.web.exception_handler
    @winter.web.response_status(HTTPStatus.FORBIDDEN)
    def handle_access_denied(self, exception: TodoAccessDeniedException) -> ErrorDTO:
        return ErrorDTO(index=exception.index, message='Access denied')


todo_list: List[str] = []


class TodoProblemExistsExampleAPI:
    @winter.web.route_get('problem/{todo_index}/')
    @winter.web.raises(TodoNotFoundException)  # Declares the response in the OpenAPI spec
    def get_todo(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

    @winter.web.route_get('denied/{todo_index}/')
    @winter.web.raises(TodoAccessDeniedException)
    def get_denied_todo(self, todo_index: int):
        raise TodoAccessDeniedException(index=todo_index)

```


## Interceptors
You can define interceptors to pre-handle a web request before it gets to an endpoint code.
The pre_handle method arguments are resolved the same way as those of an API method, and `method` receives the API
method of the request.
It's not supported to return any response from interceptors.
However, the exceptions thrown from within an interceptor will be handled automatically.
```python
import winter.web
from winter.components import ComponentMethod
from winter.web import Interceptor
from winter.web import Request
from winter.web import ResponseHeader


class HelloWorldInterceptor(Interceptor):
    @winter.web.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(self, method: ComponentMethod, request: Request, hello_world_header: ResponseHeader[str]):
        print(f'Method: {method.name}')
        if 'hello_world' in request.query_parameters:
            hello_world_header.set('Hello, World!')

```

An application lists the classes of its interceptors in the order they run. The injector of each request creates
them, so their dependencies go to `__init__`:
```python
app = winter.web.WebApplication(modules=[some_package], interceptors=[HelloWorldInterceptor])
```

## Values from the injector
An argument that is not mapped from the request (path and query parameters, `@request_body`, `@request_header`,
`@response_header`, `PagePosition`) comes from the injector of the application, which must bind its type:
otherwise the application fails on startup. The dependencies of the class itself go to `__init__`, where the
injector creates them without bindings. A provider marked `@winter.web.request_scope` is called once per request,
and its value exists only while Winter handles a request. Every request binds `winter.web.Request` and, under
Django, `django.http.HttpRequest`.
```python
import injector
import winter.web
from django.http import HttpRequest


class AccountModule(injector.Module):
    @injector.provider
    @winter.web.request_scope
    def account(self, request: HttpRequest, accounts: AccountQueries) -> Account:
        return accounts.get(request.user.pk)


class ProfileAPI:
    @injector.inject
    def __init__(self, profiles: ProfileQueries):
        self._profiles = profiles

    @winter.web.route_get('profile/')
    def get(self, account: Account) -> ProfileDTO:
        return self._profiles.get(account)


app = winter.web.WebApplication(modules=[profiles], injector=injector.Injector([AccountModule()]))
```

Interceptors and exception handlers of a request get the same request-scoped values as its API method.

## Undefined JSON fields

By default, if a JSON request contains a field that is not defined in a dataclass, an exception will be thrown.
To accept missing fields in dataclass, you can use Undefined class to explicitly mark fields as optional.

```python
import winter.web
from dataclasses import dataclass
from typing import Union
from winter.json import Undefined


@dataclass
class RequestBody:
    field_a: Union[str, Undefined]
    field_b: Union[str, Undefined] = Undefined()  # explicit default value is not required


class SomeAPI:
    @winter.web.route_post('/')
    @winter.web.request_body('body')
    def some_method(self, body: RequestBody):
        if body.field_a == Undefined():
            print('Field A is not defined in JSON request')
        if body.field_b == Undefined():
            print('Field B is not defined in JSON request')
```