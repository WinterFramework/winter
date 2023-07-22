from django.http import HttpResponse

import winter
from winter.web import MediaType


@winter.route('with-media-types-routing/')
class APIWithMediaTypesRouting:
    @winter.route_get('xml/', produces=(MediaType.APPLICATION_XML, ))
    def get_xml(self) -> HttpResponse:
        return HttpResponse(b'Hello, sir!', content_type=str(MediaType.APPLICATION_XML))
