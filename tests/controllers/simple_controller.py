import winter


@winter.controller
@winter.route('winter_simple/')
class SimpleController:

    @winter.route_get()
    @winter.query_parameter('name')
    def hello(self, name: str = 'stranger') -> str:
        return f'Hello, {name}!'
