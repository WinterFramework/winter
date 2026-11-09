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

# Upgrading

- [Upgrading to Winter 34](docs/upgrading-to-34.md)
- [Upgrading to Winter 33](docs/upgrading-to-33.md)

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

The fields of a subclass go to the meta of the JSON and of the OpenAPI spec, so a subclass can add links
to the previous and the next pages, built from the request:
```python
from dataclasses import dataclass
from typing import Generic
from typing import Optional
from typing import TypeVar

from furl import furl

import winter.web
from winter.pagination import Page
from winter.pagination import PagePosition


T = TypeVar('T')

@dataclass(frozen=True)
class LinkedPage(Page, Generic[T]):
    previous: Optional[str]
    next: Optional[str]

    @classmethod
    def of(cls, page: Page[T], request: winter.web.Request) -> 'LinkedPage[T]':
        limit = page.position.limit
        offset = page.position.offset or 0
        has_previous = limit is not None and offset > 0
        has_next = limit is not None and offset + limit < page.total_count
        return cls(
            total_count=page.total_count,
            items=page.items,
            position=page.position,
            previous=_page_url(request, limit, max(offset - limit, 0)) if has_previous else None,
            next=_page_url(request, limit, offset + limit) if has_next else None,
        )


def _page_url(request: winter.web.Request, limit: int, offset: int) -> str:
    url = furl(request.full_path)
    url.args['limit'] = limit
    if offset:
        url.args['offset'] = offset
    else:
        url.args.pop('offset', None)
    return url.tostr()


class TodoAPI:
    @winter.web.route_get('todos/')
    def get_todos(self, request: winter.web.Request, page_position: PagePosition) -> LinkedPage[int]:
        page = Page(total_count=3, items=[1, 2, 3], position=page_position)
        return LinkedPage.of(page, request)
```

`PagePosition` comes from `limit`, `offset` and `order_by`. Other parameters of a page are a dataclass of query
parameters, which the route declares for the request and for the OpenAPI spec alike:
```python
from dataclasses import dataclass

import winter.web
from winter.pagination import Page
from winter.pagination import PagePosition


@dataclass
class PageNumber:
    page_size: int = 20
    page_number: int = 1

    def position(self) -> PagePosition:
        return PagePosition(limit=self.page_size, offset=(self.page_number - 1) * self.page_size)


class TodoAPI:
    @winter.web.route_get('todos/{?page_size,page_number}')
    @winter.web.query_parameters('page')
    def get_todos(self, page: PageNumber) -> Page[int]:
        return Page(total_count=3, items=[1, 2, 3], position=page.position())
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
    # application. The class is created by the injector. An exception without a handler goes to the host, such as
    # Django or a WSGI server, which logs it and answers 500; a handler of Exception gives a response of its own.
    @winter.web.exception_handler
    @winter.web.response_status(HTTPStatus.FORBIDDEN)
    def handle_access_denied(self, exception: TodoAccessDeniedException) -> ErrorDTO:
        return ErrorDTO(index=exception.index, message='Access denied')


todo_list: List[str] = []


class TodoProblemExistsExampleAPI:
    @winter.web.route_get('problem/{todo_index}/')
    # Declares the response in the OpenAPI spec. The application must have a handler of the exception.
    @winter.web.raises(TodoNotFoundException)
    def get_todo(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

    @winter.web.route_get('denied/{todo_index}/')
    @winter.web.raises(TodoAccessDeniedException)
    def get_denied_todo(self, todo_index: int):
        raise TodoAccessDeniedException(index=todo_index)

```


## Interceptors
You can define interceptors to pre-handle a web request before it gets to an endpoint code.
The pre_handle method arguments are resolved the same way as those of an API method: a `winter.web.Route` argument
gets the route of the request, whose `method` is the API method with its annotations.
It's not supported to return any response from interceptors.
However, the exceptions thrown from within an interceptor will be handled automatically.
```python
import winter.web
from winter.web import Interceptor
from winter.web import Request
from winter.web import ResponseHeader
from winter.web import Route


class HelloWorldInterceptor(Interceptor):
    @winter.web.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(self, route: Route, request: Request, hello_world_header: ResponseHeader[str]):
        print(f'Method: {route.method.name}')
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
and its value exists only while Winter handles a request. Every request binds `winter.web.Request`, its
`winter.web.Route`, whose `method` is the API method with its annotations, and, under Django, `django.http.HttpRequest`.
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