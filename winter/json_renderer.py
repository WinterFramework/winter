from rest_framework.renderers import JSONRenderer

from .json_encoder import WinterJSONEncoder


class WinterJSONRenderer(JSONRenderer):
    encoder_class = WinterJSONEncoder
