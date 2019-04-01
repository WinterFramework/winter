import winter
from winter.exceptions import RedirectException


@winter.route_get('with-redirect-exception/')
class ControllerWithRedirectException:

    @winter.route_get()
    def get(self):
        raise RedirectException('http://1.2.3.4/')
