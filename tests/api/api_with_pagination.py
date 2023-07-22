from typing import Any
from typing import Dict

import winter
from winter.data.pagination import PagePosition


@winter.route('paginated/')
class APIWithPagination:

    @winter.route_get('with-limits/')
    @winter.web.pagination.limits(default=20, maximum=100, redirect_to_default=True)
    def method1(self, page_position: PagePosition) -> Dict[str, Any]:
        return {
            'limit': page_position.limit,
            'offset': page_position.offset,
        }

    @winter.route_get('')
    @winter.web.pagination.order_by(['id', 'name'], default_sort=('name',))
    def method2(self, page_position: PagePosition) -> Dict[str, Any]:
        return {
            'limit': page_position.limit,
            'offset': page_position.offset,
            'sort': str(page_position.sort) if page_position.sort else None,
        }
