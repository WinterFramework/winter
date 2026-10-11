from django.shortcuts import render

from winter.web import Request
from winter.web.output_processor import IOutputProcessor
from winter.web.output_processor import register_output_processor
from .request import DjangoRequest


class TemplateRenderer(IOutputProcessor):

    def __init__(self, template_name: str):
        self._template_name = template_name

    def process_output(self, output, request: Request):
        assert isinstance(request, DjangoRequest), 'output_template works with the Django adapter only'
        return render(request.django_request, self._template_name, context=output)


def output_template(template_name: str):
    def wrapper(func):
        output_processor = TemplateRenderer(template_name)
        return register_output_processor(func, output_processor)

    return wrapper
