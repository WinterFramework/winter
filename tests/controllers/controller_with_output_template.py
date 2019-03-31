import winter


@winter.controller
@winter.route('with-output-template/')
class ControllerWithOutputTemplate:

    @winter.route_get()
    @winter.query_parameter('name')
    @winter.output_template('hello.txt')
    def greet(self, name: str):
        return {'name': name}
