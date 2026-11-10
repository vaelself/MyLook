"""CallbackData-фабрики. В колбэках передаём только ID и короткие коды (лимит 64 байта)."""

from aiogram.filters.callback_data import CallbackData


class NavCb(CallbackData, prefix="nav"):
    # action: main, cancel, add_item, add_place, shop, edit_city
    action: str


class ItemCb(CallbackData, prefix="item"):
    # action: list, page, open, name, type, cat, photo, places, del, del_yes, del_no
    action: str
    item_id: int = 0
    page: int = 0


class TypeCb(CallbackData, prefix="type"):
    code: str
    item_id: int = 0  # 0 — выбор типа при добавлении новой вещи


class PlaceCb(CallbackData, prefix="place"):
    # action: list, page, open, rename, items, del, del_yes, del_no
    action: str
    place_id: int = 0
    page: int = 0


class CheckCb(CallbackData, prefix="check"):
    # мультивыбор; action: toggle, page, done, skip
    action: str
    id: int = 0
    page: int = 0


class OutfitCb(CallbackData, prefix="outfit"):
    # action: pick, page, again
    action: str
    place_id: int = 0
    page: int = 0
