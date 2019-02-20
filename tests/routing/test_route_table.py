import winter
from winter.controller import get_controller_component
from winter.routing import Route
from winter.routing import route_table


@winter.controller
@winter.route('/route_tables')
class Controller1:
    @winter.route_get('/')
    def get_list(self):
        pass

    @winter.route_get('/{id}/')
    def get_detail(self):
        pass


@winter.controller
class Controller2:
    @winter.route_post('/route_tables/')
    def create(self):
        pass


def test_route_table_collects_routes():
    routes = route_table.get_routes()

    get_list = get_controller_component(Controller1).get_method('get_list')
    get_detail = get_controller_component(Controller1).get_method('get_detail')
    create = get_controller_component(Controller2).get_method('create')

    assert Route('GET', '/route_tables/', Controller1, get_list) in routes
    assert Route('GET', '/route_tables/{id}/', Controller1, get_detail) in routes
    assert Route('POST', '/route_tables/', Controller2, create) in routes
