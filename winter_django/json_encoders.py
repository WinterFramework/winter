from django.utils.functional import Promise

from winter.json.encoder import register_encoder


@register_encoder
def promise_encoder(promise: Promise):
    return str(promise)
