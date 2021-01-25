# Winter

[![Build Status](https://travis-ci.org/WinterFramework/winter.svg?branch=master)](https://travis-ci.org/WinterFramework/winter)
[![codecov](https://codecov.io/gh/WinterFramework/winter/branch/master/graph/badge.svg)](https://codecov.io/gh/WinterFramework/winter)
[![Maintainability](https://api.codeclimate.com/v1/badges/876abe42ca943d9c6014/maintainability)](https://codeclimate.com/github/WinterFramework/winter/maintainability)
[![PyPI version](https://badge.fury.io/py/winter.svg)](https://badge.fury.io/py/winter)
[![Gitter](https://badges.gitter.im/winter-python/community.svg)](https://gitter.im/winter-python/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Web Framework for Python inspired by Spring Framework

# Main features
* Declarative API
* Built around python type annotations
* Automatic OpenAPI (swagger) documentation generation
* Suitable for DDD
* Handling exception without boilerplate in accordance with [RFC 7807](https://tools.ietf.org/html/rfc7807)

# How to use
## Installation
```
pip install winter
```

## Hello world
```python
import winter

@winter.controller
class HelloWorldController:
    @winter.route_get('/hello/')
    def hello(self):
        return f'Hello, world!'
```

To use it with Django:
```python
import winter_django

urlpatterns = [
    *winter_django.create_django_urls(HelloWorldController),
]
```

## Todo list CRUD example:
```python
from http import HTTPStatus
from typing import List
from typing import Optional

import winter
import winter.web
from dataclasses import dataclass
from winter.data.pagination import Page
from winter.data.pagination import PagePosition


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


@winter.web.controller
@winter.route('todo/')
class TodoController:
    @winter.route_post('')
    @winter.request_body(argument_name='new_todo_dto')
    def create_todo(self, new_todo_dto: NewTodoDTO) -> TodoDTO:
        todo_list.append(new_todo_dto.todo)
        return self._build_todo_dto(len(todo_list) - 1)

    @winter.route_get('{todo_index}/')
    def get_todo(self, todo_index: int) -> TodoDTO:
        self._check_index(todo_index)
        return self._build_todo_dto(todo_index)

    @winter.route_get('{?q}')
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

    @winter.route_get('{todo_index}/')
    @winter.request_body(argument_name='todo_update_dto')
    def update_todo(self, todo_index: int, todo_update_dto: TodoUpdateDTO):
        self._check_index(todo_index)
        todo_list[todo_index] = todo_update_dto.todo

    @winter.route_get('{todo_index}/')
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
import winter
import winter.web
from dataclasses import dataclass
from winter.data.pagination import Page
from winter.data.pagination import PagePosition
from typing import TypeVar
from typing import Generic


T = TypeVar('T')

@dataclass(frozen=True)
class CustomPage(Page, Generic[T]):
    extra_field: str  # The field will go to meta JSON response field


@winter.web.controller
class ExampleController:
    @winter.route_get('/')
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

from rest_framework.request import Request
import winter
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
    @winter.response_status(HTTPStatus.NOT_FOUND)
    def handle(self, request: Request, exception: TodoNotFoundException) -> ErrorDTO:
        return ErrorDTO(index=exception.invalid_index, message='Access denied')


todo_list: List[str] = []


@winter.web.controller
class TodoProblemExistsController:
    @winter.route_get('global/{todo_index}/')
    def get_todo_with_global_handling(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

    @winter.route_get('custom/{todo_index}/')
    @winter.raises(TodoNotFoundException, handler_cls=TodoNotFoundExceptionCustomHandler)
    def get_todo_with_custom_handling(self, todo_index: int):
        raise TodoNotFoundException(invalid_index=todo_index)

```


## Interceptors
You can define interceptors to pre-handle a web request before it gets to a controller.
The pre_handle method arguments will be injected the same way as it's done in controllers.
It's not supported to return any response from interceptors.
However, the exceptions thrown from within an interceptor will be handled automatically.
```python
from rest_framework.request import Request
import winter
from winter.web import Interceptor
from winter.web import ResponseHeader


class HelloWorldInterceptor(Interceptor):
    @winter.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(self, request: Request, hello_world_header: ResponseHeader[str]):
        if 'hello_world' in request.query_params:
            hello_world_header.set('Hello, World!')

```


The only way now to register an interceptor is to define a configurer
(don't forget to import during app initialization) and implement the add_interceptors method.
```python
from winter.web import Configurer
from winter.web import InterceptorRegistry

from .interceptors import HelloWorldInterceptor


class HelloWorldConfigurer(Configurer):
    def add_interceptors(self, registry: InterceptorRegistry):
        registry.add_interceptor(HelloWorldInterceptor())

```
