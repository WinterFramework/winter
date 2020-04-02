from typing import Any
from typing import Dict

import winter


@winter.controller
@winter.route('with-output-template/')
class ControllerWithOutputTemplate:

    @winter.route_get('{?name}')
    @winter.output_template('hello.txt')
    def greet(self, name: str) -> Dict[str, Any]:
        return {'name': name}
