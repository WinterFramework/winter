# Winter

[![Build Status](https://travis-ci.org/mofr/winter.svg?branch=master)](https://travis-ci.org/mofr/winter)
[![codecov](https://codecov.io/gh/mofr/winter/branch/master/graph/badge.svg)](https://codecov.io/gh/mofr/winter)
[![Maintainability](https://api.codeclimate.com/v1/badges/c6b0b8dfbe97cfa378a3/maintainability)](https://codeclimate.com/github/mofr/winter/maintainability)
[![PyPI version](https://badge.fury.io/py/winter.svg)](https://badge.fury.io/py/winter)
[![Gitter](https://badges.gitter.im/winter-python/community.svg)](https://gitter.im/winter-python/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Web Framework for Python inspired by Spring Framework

# Main features
* Declarative API
* Built around python type annotations
* Automatic OpenAPI (swagger) documentation generation
* Suitable for DDD

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
import winter.django

urlpatterns = [
    *winter.django.create_django_urls(HelloWorldController),
]
```

To implement CRUD:
```python
from http import HTTPStatus
from typing import List
from typing import Optional

import winter
from dataclasses import dataclass
from rest_framework.request import Request
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


class NotFoundException(Exception):
    def __init__(self, todo_index: int):
        self.index = todo_index


class NotFoundExceptionHandler(winter.ExceptionHandler):
    @winter.response_status(HTTPStatus.NOT_FOUND)
    def handle(self, request: Request, exception: NotFoundException) -> str:
        return f'Index {exception.index} out of bounds'


todo_list: List[str] = []


@winter.controller
@winter.route('todo/')
class TodoController:
    @winter.route_post('')
    @winter.request_body(argument_name='new_todo_dto')
    def create_todo(self, new_todo_dto: NewTodoDTO) -> TodoDTO:
        todo_list.append(new_todo_dto.todo)
        return self._build_todo_dto(len(todo_list) - 1)

    @winter.route_get('{todo_index}/')
    @winter.throws(NotFoundException, handler_cls=NotFoundExceptionHandler)
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
    @winter.throws(NotFoundException, handler_cls=NotFoundExceptionHandler)
    def update_todo(self, todo_index: int, todo_update_dto: TodoUpdateDTO):
        self._check_index(todo_index)
        todo_list[todo_index] = todo_update_dto.todo

    @winter.route_get('{todo_index}/')
    @winter.throws(NotFoundException, handler_cls=NotFoundExceptionHandler)
    def delete_todo(self, todo_index: int):
        self._check_index(todo_index)
        del todo_list[todo_index]

    def _check_index(self, todo_index: int):
        if todo_index < 0 or todo_index >= len(todo_list):
            raise NotFoundException(todo_index=todo_index)

    def _build_todo_dto(self, todo_index: int):
        return TodoDTO(todo_index=todo_index, todo=todo_list[todo_index])
```
