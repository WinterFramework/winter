from typing import Any
from typing import Dict

import winter
import winter_django


@winter.route('with-output-template/')
class APIWithOutputTemplate:

    @winter.route_get('{?name}')
    @winter_django.output_template('hello.txt')
    def greet(self, name: str) -> Dict[str, Any]:
        return {'name': name}
