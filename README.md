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

To use it with Django:
```python
from winter.web.autodiscovery import find_package_routes
import winter.django

routes = find_package_routes('some_package.sub_package')
urlpatterns = [
    *winter.django.create_django_urls_from_routes(routes),
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

from django.http import HttpRequest

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

# When we want to override global handler and customize response body. Expected output below:
# {index: 1, 'message': 'Access denied'}
@dataclass
class ErrorDTO:
    index: int
    message: str


class TodoNotFoundExceptionCustomHandler(winter.web.ExceptionHandler):
    @winter.web.response_status(HTTPStatus.NOT_FOUND)
    def handle(self, request: HttpRequest, exception: TodoNotFoundException) -> ErrorDTO:
        return ErrorDTO(index=exception.invalid_index, message='Access denied')


todo_list: List[str] = []


class TodoProblemExistsExampleAPI:
    @winter.web.route_get('global/{todo_index}/')
    def get_todo_with_global_handling(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

    @winter.web.route_get('custom/{todo_index}/')
    @winter.web.raises(TodoNotFoundException, handler_cls=TodoNotFoundExceptionCustomHandler)
    def get_todo_with_custom_handling(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

```


## Interceptors
You can define interceptors to pre-handle a web request before it gets to an endpoint code.
The pre_handle method arguments will be injected the same way as it's done in methods with winter.web.route annotation.
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


The only way now to register an interceptor is to add it to InterceptorRegistry singleton.

Don't forget to import this adding during app initialization.
```python
from winter.web import interceptor_registry
from .interceptors import HelloWorldInterceptor

class SomeInitializationClassInMyApplication:
    def initialize_my_app(self):
        interceptor_registry.add_interceptor(HelloWorldInterceptor())

```

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