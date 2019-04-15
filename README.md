# Winter

[![Build Status](https://travis-ci.org/mofr/winter.svg?branch=master)](https://travis-ci.org/mofr/winter)
[![codecov](https://codecov.io/gh/mofr/winter/branch/master/graph/badge.svg)](https://codecov.io/gh/mofr/winter)
[![Maintainability](https://api.codeclimate.com/v1/badges/c6b0b8dfbe97cfa378a3/maintainability)](https://codeclimate.com/github/mofr/winter/maintainability)
[![PyPI version](https://badge.fury.io/py/winter.svg)](https://badge.fury.io/py/winter)

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
