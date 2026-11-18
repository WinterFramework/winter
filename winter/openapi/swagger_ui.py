import json
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Optional

import winter.web


def swagger_ui_response(
    *,
    spec_url: str,
    title: str = 'Swagger UI',
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    swagger_favicon_url: str = "https://static1.smartbear.co/swagger/media/assets/swagger_fav.png",
    swagger_ui_parameters: Optional[Dict[str, Any]] = None,
) -> winter.web.Response:
    """
    The page of Swagger UI for the spec at `spec_url`, for an API method to return. The method declares the route and
    whatever else the application needs, such as its own annotations. Stolen from FastAPI.
    """
    current_swagger_ui_parameters = {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    }
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{spec_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(value)},\n"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""

    html += """
    </script>
    </body>
    </html>
    """
    return winter.web.Response(HTTPStatus.OK, html.encode(), {'content-type': 'text/html'})
