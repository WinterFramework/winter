import winter.openapi
import winter.web


class SwaggerUI:
    @winter.web.route_get('swagger-ui/')
    def get_swagger_ui(self) -> winter.web.Response:
        return winter.openapi.swagger_ui_response(spec_url='http://testserver/openapi.yml')

    @winter.web.route_get('swagger-ui-with-params/')
    def get_swagger_ui_with_custom_parameters(self) -> winter.web.Response:
        return winter.openapi.swagger_ui_response(
            spec_url='http://testserver/openapi.yml',
            swagger_ui_parameters={'deepLinking': False},
        )
