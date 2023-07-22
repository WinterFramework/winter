import django.http
from django.shortcuts import render

from winter.web.output_processor import IOutputProcessor
from winter.web.output_processor import register_output_processor


class TemplateRenderer(IOutputProcessor):

    def __init__(self, template_name: str):
        self._template_name = template_name

    def process_output(self, output, request: django.http.HttpRequest):
        return render(request, self._template_name, context=output)


def output_template(template_name: str):
    def wrapper(func):
        output_processor = TemplateRenderer(template_name)
        return register_output_processor(func, output_processor)

    return wrapper
