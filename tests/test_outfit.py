import random

from outfit import build_outfits

PLACE = 1
OTHER_PLACE = 2


def make_item(item_id, item_type, places=(PLACE,)):
    return {"id": item_id, "name": f"вещь {item_id}", "type": item_type,
            "category": "кат", "photo_file_id": "x", "places": list(places)}


def ids(outfit):
    return {item["id"] for item in outfit}


def test_two_different_outfits():
    items = [make_item(1, "top"), make_item(2, "top"), make_item(3, "bottom"), make_item(4, "shoes")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert len(result.outfits) == 2
    assert ids(result.outfits[0]) != ids(result.outfits[1])


def test_only_one_outfit_possible():
    items = [make_item(1, "top"), make_item(2, "bottom"), make_item(3, "shoes")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert len(result.outfits) == 1
    assert ids(result.outfits[0]) == {1, 2, 3}


def test_missing_shoes():
    items = [make_item(1, "top"), make_item(2, "bottom")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert result.outfits == []
    assert result.missing == ["shoes"]


def test_missing_bottom():
    items = [make_item(1, "top"), make_item(2, "shoes")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert result.missing == ["bottom"]


def test_missing_top_bottom_and_one_piece():
    items = [make_item(1, "shoes"), make_item(2, "accessory")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert result.missing == ["top", "bottom"]


def test_no_items_for_place():
    items = [make_item(1, "top", places=[OTHER_PLACE])]
    result = build_outfits(items, PLACE, random.Random(1))
    assert result.no_items
    assert result.outfits == []


def test_items_from_other_place_not_used():
    items = [make_item(1, "top"), make_item(2, "bottom"), make_item(3, "shoes"),
             make_item(4, "top", places=[OTHER_PLACE]), make_item(5, "outerwear", places=[OTHER_PLACE])]
    result = build_outfits(items, PLACE, random.Random(1))
    for outfit in result.outfits:
        assert 4 not in ids(outfit)
        assert 5 not in ids(outfit)


def test_one_piece_and_shoes():
    items = [make_item(1, "one_piece"), make_item(2, "shoes")]
    result = build_outfits(items, PLACE, random.Random(1))
    assert len(result.outfits) == 1
    assert ids(result.outfits[0]) == {1, 2}


def test_extras_added_only_if_exist():
    items = [make_item(1, "top"), make_item(2, "bottom"), make_item(3, "shoes")]
    result = build_outfits(items, PLACE, random.Random(1))
    types = [item["type"] for item in result.outfits[0]]
    assert "outerwear" not in types and "accessory" not in types

    items += [make_item(4, "outerwear"), make_item(5, "accessory")]
    result = build_outfits(items, PLACE, random.Random(1))
    types = [item["type"] for item in result.outfits[0]]
    # порядок вывода: верхняя одежда -> верх -> низ -> обувь -> аксессуар
    assert types == ["outerwear", "top", "bottom", "shoes", "accessory"]


def test_same_seed_same_result():
    items = [make_item(i, t) for i, t in enumerate(["top", "top", "top", "bottom", "bottom",
                                                     "shoes", "shoes", "accessory", "accessory"])]
    first = build_outfits(items, PLACE, random.Random(42))
    second = build_outfits(items, PLACE, random.Random(42))
    assert [ids(o) for o in first.outfits] == [ids(o) for o in second.outfits]
