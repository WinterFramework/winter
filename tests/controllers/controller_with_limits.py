from typing import Any
from typing import Dict

import winter
from winter.data.pagination import PagePosition


@winter.route('with-limits/')
class ControllerWithLimits:

    @winter.route_get('')
    @winter.web.pagination.limits(default=20, maximum=100, redirect_to_default=True)
    def method(self, page_position: PagePosition) -> Dict[str, Any]:
        return {
            'limit': page_position.limit,
            'offset': page_position.offset,
        }
