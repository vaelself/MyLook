"""Небольшие вспомогательные функции, которые нужны в разных модулях."""

from constants import ITEM_TYPES, PAGE_SIZE


def clean_text(text: str, max_len: int) -> str | None:
    """Обрезает пробелы и проверяет длину. Возвращает None, если длина не подходит."""
    text = text.strip()
    if 1 <= len(text) <= max_len:
        return text
    return None


def paginate(elements: list, page: int) -> tuple[list, int, int]:
    """Возвращает элементы нужной страницы, номер страницы и число страниц."""
    pages = max(1, (len(elements) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(max(page, 0), pages - 1)
    start = page * PAGE_SIZE
    return elements[start:start + PAGE_SIZE], page, pages


def sorted_items(items: list[dict]) -> list[dict]:
    """Вещи по порядку типов (как в ITEM_TYPES), внутри — по названию."""
    type_order = list(ITEM_TYPES)
    return sorted(items, key=lambda item: (type_order.index(item["type"]), item["name"].lower()))
