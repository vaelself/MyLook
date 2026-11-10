"""Ссылки на поиск вещи в интернет-магазинах."""

from urllib.parse import quote

SHOPS = [
    ("Wildberries", "https://www.wildberries.ru/catalog/0/search.aspx?search={q}"),
    ("Ozon", "https://www.ozon.ru/search/?text={q}"),
    ("Lamoda", "https://www.lamoda.ru/catalogsearch/result/?q={q}"),
]


def build_shop_links(query: str) -> list[tuple[str, str]]:
    """Возвращает список (название магазина, ссылка на поиск)."""
    q = quote(query.strip())
    return [(name, url.format(q=q)) for name, url in SHOPS]
