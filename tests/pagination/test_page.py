from winter.pagination import Page
from winter.pagination import PagePosition


def test_iter_page():
    page_position = PagePosition()
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    page = Page(10, items, page_position)

    # Act
    page_items = list(page)

    # Assert
    assert page_items == items
