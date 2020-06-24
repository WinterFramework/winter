from rest_framework import renderers

from winter.core.json import JSONEncoder


class JSONRenderer(renderers.JSONRenderer):
    encoder_class = JSONEncoder
