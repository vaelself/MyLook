"""Функции, которые строят клавиатуры."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import texts
from callbacks import CheckCb, ItemCb, NavCb, OutfitCb, PlaceCb, TypeCb
from constants import ITEM_TYPES
from utils import paginate


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=texts.BTN_WARDROBE)
    builder.button(text=texts.BTN_ADD_ITEM)
    builder.button(text=texts.BTN_PLACES)
    builder.button(text=texts.BTN_OUTFIT)
    builder.button(text=texts.BTN_SHOP)
    builder.button(text=texts.BTN_SETTINGS)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def button(text: str, callback: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback.pack())


def main_menu_button() -> InlineKeyboardButton:
    return button(texts.BTN_MAIN_MENU, NavCb(action="main"))


def cancel_button() -> InlineKeyboardButton:
    return button(texts.BTN_CANCEL, NavCb(action="cancel"))


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button()]])


def add_pager(builder: InlineKeyboardBuilder, page: int, pages: int, make_cb) -> None:
    """Добавляет кнопки ◀️ / ▶️, если страниц больше одной.
    make_cb(номер_страницы) должна вернуть CallbackData для этой страницы."""
    row = []
    if page > 0:
        row.append(button(texts.BTN_PREV, make_cb(page - 1)))
    if page < pages - 1:
        row.append(button(texts.BTN_NEXT, make_cb(page + 1)))
    if row:
        builder.row(*row)


# ---------- вещи ----------

def types_kb(item_id: int = 0) -> InlineKeyboardMarkup:
    """Выбор типа. item_id=0 — при добавлении, иначе — при изменении вещи."""
    builder = InlineKeyboardBuilder()
    for code, name in ITEM_TYPES.items():
        builder.button(text=name, callback_data=TypeCb(code=code, item_id=item_id))
    builder.adjust(2)
    if item_id == 0:
        builder.row(cancel_button())
    else:
        builder.row(button(texts.BTN_BACK, ItemCb(action="open", item_id=item_id)))
    return builder.as_markup()


def wardrobe_kb(page_items: list[dict], page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in page_items:
        builder.row(button(f"{item['name']} ({item['category']})",
                           ItemCb(action="open", item_id=item["id"], page=page)))
    add_pager(builder, page, pages, lambda p: ItemCb(action="page", page=p))
    builder.row(main_menu_button())
    return builder.as_markup()


def empty_wardrobe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_ADD_FIRST_ITEM, NavCb(action="add_item"))],
        [main_menu_button()],
    ])


def item_card_kb(item_id: int) -> InlineKeyboardMarkup:
    def item_button(text: str, action: str) -> InlineKeyboardButton:
        return button(text, ItemCb(action=action, item_id=item_id))

    return InlineKeyboardMarkup(inline_keyboard=[
        [item_button(texts.BTN_EDIT_NAME, "name"), item_button(texts.BTN_EDIT_TYPE, "type")],
        [item_button(texts.BTN_EDIT_CATEGORY, "cat"), item_button(texts.BTN_EDIT_PHOTO, "photo")],
        [item_button(texts.BTN_EDIT_PLACES, "places"), item_button(texts.BTN_DELETE, "del")],
        [item_button(texts.BTN_TO_LIST, "list")],
    ])


def confirm_kb(yes_cb: CallbackData, no_cb: CallbackData) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_YES_DELETE, yes_cb), button(texts.BTN_CANCEL, no_cb)],
    ])


def multiselect_kb(options: list[tuple[int, str]], selected: list[int], page: int,
                   with_skip: bool = False) -> InlineKeyboardMarkup:
    """Мультивыбор: options — список (id, подпись), selected — отмеченные id."""
    builder = InlineKeyboardBuilder()
    page_options, page, pages = paginate(options, page)
    for option_id, label in page_options:
        mark = "✅" if option_id in selected else "⬜"
        builder.row(button(f"{mark} {label}", CheckCb(action="toggle", id=option_id, page=page)))
    add_pager(builder, page, pages, lambda p: CheckCb(action="page", page=p))
    last_row = [button(texts.BTN_DONE, CheckCb(action="done"))]
    if with_skip:
        last_row.append(button(texts.BTN_SKIP, CheckCb(action="skip")))
    builder.row(*last_row)
    builder.row(cancel_button())
    return builder.as_markup()


# ---------- места ----------

def places_kb(page_places: list[dict], page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in page_places:
        builder.row(button(place["name"], PlaceCb(action="open", place_id=place["id"], page=page)))
    add_pager(builder, page, pages, lambda p: PlaceCb(action="page", page=p))
    builder.row(button(texts.BTN_ADD_PLACE, NavCb(action="add_place")))
    builder.row(main_menu_button())
    return builder.as_markup()


def add_place_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_ADD_PLACE, NavCb(action="add_place"))],
        [main_menu_button()],
    ])


def place_card_kb(place_id: int) -> InlineKeyboardMarkup:
    def place_button(text: str, action: str) -> InlineKeyboardButton:
        return button(text, PlaceCb(action=action, place_id=place_id))

    return InlineKeyboardMarkup(inline_keyboard=[
        [place_button(texts.BTN_RENAME, "rename")],
        [place_button(texts.BTN_PLACE_ITEMS, "items")],
        [place_button(texts.BTN_DELETE, "del")],
        [place_button(texts.BTN_TO_LIST, "list")],
    ])


# ---------- подбор образа ----------

def outfit_places_kb(page_places: list[dict], page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in page_places:
        builder.row(button(place["name"], OutfitCb(action="pick", place_id=place["id"])))
    add_pager(builder, page, pages, lambda p: OutfitCb(action="page", page=p))
    builder.row(main_menu_button())
    return builder.as_markup()


def outfit_done_kb(place_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_AGAIN, OutfitCb(action="again", place_id=place_id))],
        [button(texts.BTN_SHOP, NavCb(action="shop"))],
        [main_menu_button()],
    ])


def outfit_fail_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_ADD_ITEM, NavCb(action="add_item"))],
        [button(texts.BTN_SHOP, NavCb(action="shop"))],
        [main_menu_button()],
    ])


def add_item_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_ADD_ITEM, NavCb(action="add_item"))],
        [main_menu_button()],
    ])


# ---------- покупка и настройки ----------

def shop_kb(links: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=name, url=url)] for name, url in links]
    rows.append([main_menu_button()])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(texts.BTN_EDIT_CITY, NavCb(action="edit_city"))],
        [main_menu_button()],
    ])
