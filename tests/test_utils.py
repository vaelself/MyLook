from constants import PAGE_SIZE
from utils import clean_text, paginate, sorted_items


def test_clean_text_strips_spaces():
    assert clean_text("  Футболка  ", 50) == "Футболка"


def test_clean_text_rejects_empty_and_too_long():
    assert clean_text("   ", 50) is None
    assert clean_text("a" * 51, 50) is None
    assert clean_text("a" * 50, 50) == "a" * 50


def test_paginate_first_and_last_page():
    elements = list(range(PAGE_SIZE + 3))
    page_items, page, pages = paginate(elements, 0)
    assert page_items == elements[:PAGE_SIZE]
    assert (page, pages) == (0, 2)

    page_items, page, pages = paginate(elements, 1)
    assert page_items == elements[PAGE_SIZE:]
    assert (page, pages) == (1, 2)


def test_paginate_page_out_of_range():
    elements = list(range(3))
    assert paginate(elements, 99)[1] == 0
    assert paginate(elements, -5)[1] == 0


def test_paginate_empty_list():
    assert paginate([], 0) == ([], 0, 1)


def test_sorted_items_by_type_then_name():
    items = [
        {"name": "кеды", "type": "shoes"},
        {"name": "Футболка", "type": "top"},
        {"name": "джинсы", "type": "bottom"},
        {"name": "Майка", "type": "top"},
    ]
    names = [item["name"] for item in sorted_items(items)]
    assert names == ["Майка", "Футболка", "джинсы", "кеды"]
