import asyncio

from storage import Storage

USER = 111
OTHER_USER = 222


def test_item_survives_restart(tmp_path):
    path = tmp_path / "wardrobe.json"
    db = Storage(str(path))
    item = asyncio.run(db.add_item(USER, "Футболка", "top", "Футболка", "photo1", []))
    asyncio.run(db.update_item(USER, item["id"], "name", "Чёрная футболка"))

    # "перезапуск" — новый объект читает тот же файл
    db2 = Storage(str(path))
    saved = db2.get_item(USER, item["id"])
    assert saved["name"] == "Чёрная футболка"

    asyncio.run(db2.delete_item(USER, item["id"]))
    db3 = Storage(str(path))
    assert db3.get_items(USER) == []


def test_delete_place_keeps_items(tmp_path):
    db = Storage(str(tmp_path / "w.json"))
    place = asyncio.run(db.add_place(USER, "Вуз"))
    item = asyncio.run(db.add_item(USER, "Джинсы", "bottom", "Джинсы", "p", [place["id"]]))

    asyncio.run(db.delete_place(USER, place["id"]))

    assert db.get_places(USER) == []
    assert db.get_item(USER, item["id"])["places"] == []


def test_set_place_items(tmp_path):
    db = Storage(str(tmp_path / "w.json"))
    place = asyncio.run(db.add_place(USER, "Вуз"))
    a = asyncio.run(db.add_item(USER, "A", "top", "к", "p", []))
    b = asyncio.run(db.add_item(USER, "B", "top", "к", "p", [place["id"]]))

    asyncio.run(db.set_place_items(USER, place["id"], [a["id"]]))

    assert db.get_item(USER, a["id"])["places"] == [place["id"]]
    assert db.get_item(USER, b["id"])["places"] == []


def test_place_name_unique_ignore_case(tmp_path):
    db = Storage(str(tmp_path / "w.json"))
    place = asyncio.run(db.add_place(USER, "Вуз"))
    assert db.place_name_exists(USER, "  вУЗ ")
    assert not db.place_name_exists(USER, "Ресторан")
    # своё же старое название при переименовании не считается дублем
    assert not db.place_name_exists(USER, "вуз", exclude_id=place["id"])


def test_users_are_isolated(tmp_path):
    db = Storage(str(tmp_path / "w.json"))
    asyncio.run(db.add_item(USER, "Моя вещь", "top", "к", "p", []))
    asyncio.run(db.set_city(USER, "Москва"))

    assert db.get_items(OTHER_USER) == []
    assert db.get_user(OTHER_USER)["city"] is None


def test_ids_not_reused(tmp_path):
    db = Storage(str(tmp_path / "w.json"))
    first = asyncio.run(db.add_item(USER, "A", "top", "к", "p", []))
    asyncio.run(db.delete_item(USER, first["id"]))
    place = asyncio.run(db.add_place(USER, "Вуз"))
    assert place["id"] != first["id"]


def test_broken_json(tmp_path):
    path = tmp_path / "wardrobe.json"
    path.write_text("{ это не json", encoding="utf-8")

    db = Storage(str(path))

    assert db.data == {"users": {}}
    broken_files = list(tmp_path.glob("wardrobe.json.broken-*"))
    assert len(broken_files) == 1
