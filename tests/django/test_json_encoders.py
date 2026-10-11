import json

from django.utils.translation import gettext_lazy

from winter.json import JSONEncoder


def test_lazy_string_is_encoded_as_its_value():
    assert json.dumps({'text': gettext_lazy('translated_text')}, cls=JSONEncoder) == '{"text": "translated_text"}'
