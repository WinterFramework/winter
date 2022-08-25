from django.http import HttpResponse

import winter
import winter_openapi


@winter.web.no_authentication
class SwaggerUI:
    @winter.route_get('swagger-ui/')
    def get_swagger_ui(self):
        html = winter_openapi.get_swagger_ui_html(
            openapi_url='http://testserver/openapi.yml',
            title='Test Swagger UI',
            swagger_ui_parameters={'deepLinking': False},
        )
        return HttpResponse(html, content_type='text/html')
