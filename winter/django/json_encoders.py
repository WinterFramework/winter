from django.utils.functional import Promise

from winter.json.encoder import json_encoder


@json_encoder
def promise_encoder(promise: Promise):
    return str(promise)
