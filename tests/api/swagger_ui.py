from django.http import HttpResponse

import winter
import winter_openapi


@winter.web.no_authentication
class SwaggerUI:
    @winter.route_get('swagger-ui/')
    def get_swagger_ui(self):
        html = winter_openapi.get_swagger_ui_html(
            openapi_url='http://testserver/openapi.yml',
        )
        return HttpResponse(html, content_type='text/html')

    @winter.route_get('swagger-ui-with-params/')
    def get_swagger_ui_with_custom_parameters(self):
        html = winter_openapi.get_swagger_ui_html(
            openapi_url='http://testserver/openapi.yml',
            swagger_ui_parameters={'deepLinking': False},
        )
        return HttpResponse(html, content_type='text/html')
