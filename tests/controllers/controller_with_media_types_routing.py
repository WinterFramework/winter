import winter
from winter.web import MediaType


@winter.controller
@winter.route('controller_with_media_types_routing/')
class ControllerWithMediaTypesRouting:

    @winter.route_get('xml/', produces=(MediaType.APPLICATION_XML, ))
    def get_xml(self) -> str:
        return 'Hello, sir!'
