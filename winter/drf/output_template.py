from django.shortcuts import render
from rest_framework.request import Request

from ..output_processor import IOutputProcessor
from ..output_processor import register_output_processor


class TemplateRenderer(IOutputProcessor):

    def __init__(self, template_name: str):
        self._template_name = template_name

    def process_output(self, output, request: Request):
        return render(request._request, self._template_name, context=output)


def output_template(template_name: str):
    def wrapper(func):
        output_processor = TemplateRenderer(template_name)
        return register_output_processor(func, output_processor)

    return wrapper
