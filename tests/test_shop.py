from shop import build_shop_links


def test_links():
    links = build_shop_links("кроссовки")
    names = [name for name, _ in links]
    assert names == ["Wildberries", "Ozon", "Lamoda"]
    assert links[1][1].startswith("https://www.ozon.ru/search/?text=")


def test_cyrillic_and_spaces_encoded():
    links = dict(build_shop_links("  белые кроссовки "))
    q = "%D0%B1%D0%B5%D0%BB%D1%8B%D0%B5%20%D0%BA%D1%80%D0%BE%D1%81%D1%81%D0%BE%D0%B2%D0%BA%D0%B8"
    assert links["Wildberries"] == f"https://www.wildberries.ru/catalog/0/search.aspx?search={q}"
    assert links["Ozon"] == f"https://www.ozon.ru/search/?text={q}"
    assert links["Lamoda"] == f"https://www.lamoda.ru/catalogsearch/result/?q={q}"
