from enum import Enum

from rest_framework.utils.encoders import JSONEncoder


class WinterJSONEncoder(JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode enums
    """
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
