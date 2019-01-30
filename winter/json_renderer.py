from rest_framework.renderers import JSONRenderer

from .json_encoder import JSONEncoder


class WinterJSONRenderer(JSONRenderer):
    encoder_class = JSONEncoder
