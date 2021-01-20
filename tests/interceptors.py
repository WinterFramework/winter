from injector import inject
from rest_framework.request import Request


class Interceptor:
    @inject
    def __init__(self):
        pass

    def pre_handle(self, request: Request):
        pass
