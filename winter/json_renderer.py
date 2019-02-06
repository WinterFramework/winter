from rest_framework import renderers

from .json_encoder import JSONEncoder


class JSONRenderer(renderers.JSONRenderer):
    encoder_class = JSONEncoder
