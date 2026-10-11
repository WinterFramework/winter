from typing import Any
from typing import Dict

import winter.web
import winter.django


@winter.web.route('with-output-template/')
class APIWithOutputTemplate:

    @winter.web.route_get('{?name}')
    @winter.django.output_template('hello.txt')
    def greet(self, name: str) -> Dict[str, Any]:
        return {'name': name}
