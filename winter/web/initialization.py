from .response_header_serializer import response_headers_serializer
from .response_header_serializers import DateTimeResponseHeaderSerializer
from .response_header_serializers import LastModifiedResponseHeaderSerializer

_process_initialized = False


def initialize():
    """
    Registers the standard response header serializers of winter.web on the first call.
    Adapters call it before building their routes.
    Process-global until these registries belong to an application: docs/architecture.md, Current deviations.
    """
    global _process_initialized
    if not _process_initialized:
        _initialize_process()
        _process_initialized = True


def _initialize_process():
    response_headers_serializer.add_serializer(DateTimeResponseHeaderSerializer())
    response_headers_serializer.add_serializer(LastModifiedResponseHeaderSerializer())
