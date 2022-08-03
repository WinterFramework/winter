import winter
from winter.web import MediaType


@winter.route('with-media-types-routing/')
class APIWithMediaTypesRouting:
    @winter.route_get('xml/', produces=(MediaType.APPLICATION_XML, ))
    def get_xml(self) -> str:
        return 'Hello, sir!'
