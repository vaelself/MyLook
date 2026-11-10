"""Места и ситуации: список, добавление, переименование, привязка вещей, удаление."""

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts
from callbacks import CheckCb, PlaceCb
from constants import MAX_PLACE_NAME
from states import AddPlace, EditPlace
from storage import Storage
from utils import clean_text, paginate, sorted_items

router = Router()


# ---------- экраны ----------

async def show_places(message: Message, user_id: int, db: Storage, page: int = 0,
                      edit: bool = False) -> None:
    """Список мест. edit=True — изменить текущее сообщение (листание страниц)."""
    places = db.get_places(user_id)
    if not places:
        text, markup = texts.PLACES_EMPTY, kb.add_place_kb()
    else:
        page_places, page, pages = paginate(places, page)
        text, markup = texts.PLACES_TITLE, kb.places_kb(page_places, page, pages)

    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def send_place_card(message: Message, user_id: int, db: Storage, place: dict,
                          header: str = "") -> None:
    count = sum(1 for item in db.get_items(user_id) if place["id"] in item["places"])
    text = texts.place_card(place, count)
    if header:
        text = header + "\n\n" + text
    await message.answer(text, reply_markup=kb.place_card_kb(place["id"]))


async def start_add_place(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddPlace.name)
    await message.answer(texts.ASK_PLACE_NAME, reply_markup=kb.cancel_kb())


def item_options(db: Storage, user_id: int) -> list[tuple[int, str]]:
    """Вещи в виде (id, подпись) для мультивыбора."""
    items = sorted_items(db.get_items(user_id))
    return [(item["id"], f"{item['name']} ({item['category']})") for item in items]


async def place_not_found(message: Message, user_id: int, db: Storage) -> None:
    await message.answer(texts.PLACE_DELETED_ALREADY)
    await show_places(message, user_id, db)


# ---------- список и карточка ----------

@router.callback_query(PlaceCb.filter(F.action == "list"))
async def place_list(callback: CallbackQuery, callback_data: PlaceCb, db: Storage) -> None:
    await callback.answer()
    await show_places(callback.message, callback.from_user.id, db, callback_data.page)


@router.callback_query(PlaceCb.filter(F.action == "page"))
async def place_list_page(callback: CallbackQuery, callback_data: PlaceCb, db: Storage) -> None:
    await callback.answer()
    await show_places(callback.message, callback.from_user.id, db, callback_data.page, edit=True)


@router.callback_query(PlaceCb.filter(F.action == "open"))
async def place_open(callback: CallbackQuery, callback_data: PlaceCb, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    place = db.get_place(user_id, callback_data.place_id)
    if place is None:
        await place_not_found(callback.message, user_id, db)
        return
    await send_place_card(callback.message, user_id, db, place)


# ---------- добавление места ----------

@router.message(AddPlace.name, F.text)
async def add_place_name(message: Message, state: FSMContext, db: Storage) -> None:
    user_id = message.from_user.id
    name = clean_text(message.text, MAX_PLACE_NAME)
    if name is None:
        await message.answer(texts.bad_length(MAX_PLACE_NAME))
        return
    if db.place_name_exists(user_id, name):
        await message.answer(texts.PLACE_EXISTS)
        return

    place = await db.add_place(user_id, name)
    options = item_options(db, user_id)
    if not options:
        # вещей нет — отмечать нечего
        await state.clear()
        await message.answer(texts.PLACE_ADDED)
        await show_places(message, user_id, db)
        return

    await state.set_state(AddPlace.items)
    await state.update_data(place_id=place["id"], selected=[])
    await message.answer(texts.ask_items_for_new_place(name),
                         reply_markup=kb.multiselect_kb(options, [], 0, with_skip=True))


# ---------- мультивыбор вещей для места ----------

@router.callback_query(StateFilter(AddPlace.items, EditPlace.items),
                       CheckCb.filter(F.action.in_({"toggle", "page"})))
async def place_items_toggle(callback: CallbackQuery, callback_data: CheckCb,
                             state: FSMContext, db: Storage) -> None:
    await callback.answer()
    data = await state.get_data()
    selected = data["selected"]
    if callback_data.action == "toggle":
        if callback_data.id in selected:
            selected.remove(callback_data.id)
        else:
            selected.append(callback_data.id)
        await state.update_data(selected=selected)

    options = item_options(db, callback.from_user.id)
    with_skip = await state.get_state() == AddPlace.items.state
    await callback.message.edit_reply_markup(
        reply_markup=kb.multiselect_kb(options, selected, callback_data.page, with_skip))


@router.callback_query(AddPlace.items, CheckCb.filter(F.action.in_({"done", "skip"})))
async def add_place_items_done(callback: CallbackQuery, callback_data: CheckCb,
                               state: FSMContext, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    # место уже создано, при «Пропустить» просто не отмечаем вещи
    if callback_data.action == "done":
        await db.set_place_items(user_id, data["place_id"], data["selected"])
    await callback.message.answer(texts.PLACE_ADDED)
    await show_places(callback.message, user_id, db)


@router.callback_query(PlaceCb.filter(F.action == "items"))
async def place_items_start(callback: CallbackQuery, callback_data: PlaceCb,
                            state: FSMContext, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    place = db.get_place(user_id, callback_data.place_id)
    if place is None:
        await place_not_found(callback.message, user_id, db)
        return

    options = item_options(db, user_id)
    if not options:
        await callback.message.answer(texts.WARDROBE_EMPTY, reply_markup=kb.empty_wardrobe_kb())
        return

    selected = [item["id"] for item in db.get_items(user_id) if place["id"] in item["places"]]
    await state.clear()
    await state.set_state(EditPlace.items)
    await state.update_data(place_id=place["id"], selected=selected)
    await callback.message.answer(texts.ASK_PLACE_ITEMS,
                                  reply_markup=kb.multiselect_kb(options, selected, 0))


@router.callback_query(EditPlace.items, CheckCb.filter(F.action == "done"))
async def place_items_done(callback: CallbackQuery, state: FSMContext, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    if not await db.set_place_items(user_id, data["place_id"], data["selected"]):
        await place_not_found(callback.message, user_id, db)
        return
    place = db.get_place(user_id, data["place_id"])
    await send_place_card(callback.message, user_id, db, place, texts.PLACE_SAVED)


# ---------- переименование ----------

@router.callback_query(PlaceCb.filter(F.action == "rename"))
async def place_rename_start(callback: CallbackQuery, callback_data: PlaceCb,
                             state: FSMContext, db: Storage) -> None:
    await callback.answer()
    if db.get_place(callback.from_user.id, callback_data.place_id) is None:
        await place_not_found(callback.message, callback.from_user.id, db)
        return
    await state.clear()
    await state.set_state(EditPlace.name)
    await state.update_data(place_id=callback_data.place_id)
    await callback.message.answer(texts.ASK_PLACE_NAME, reply_markup=kb.cancel_kb())


@router.message(EditPlace.name, F.text)
async def place_rename(message: Message, state: FSMContext, db: Storage) -> None:
    user_id = message.from_user.id
    data = await state.get_data()
    name = clean_text(message.text, MAX_PLACE_NAME)
    if name is None:
        await message.answer(texts.bad_length(MAX_PLACE_NAME))
        return
    # своё же старое название вводить можно
    if db.place_name_exists(user_id, name, exclude_id=data["place_id"]):
        await message.answer(texts.PLACE_EXISTS)
        return

    await state.clear()
    if not await db.rename_place(user_id, data["place_id"], name):
        await place_not_found(message, user_id, db)
        return
    place = db.get_place(user_id, data["place_id"])
    await send_place_card(message, user_id, db, place, texts.PLACE_SAVED)


# ---------- удаление ----------

@router.callback_query(PlaceCb.filter(F.action == "del"))
async def place_delete_ask(callback: CallbackQuery, callback_data: PlaceCb, db: Storage) -> None:
    await callback.answer()
    place = db.get_place(callback.from_user.id, callback_data.place_id)
    if place is None:
        await place_not_found(callback.message, callback.from_user.id, db)
        return
    await callback.message.answer(
        texts.confirm_delete_place(place["name"]),
        reply_markup=kb.confirm_kb(PlaceCb(action="del_yes", place_id=place["id"]),
                                   PlaceCb(action="del_no", place_id=place["id"])))


@router.callback_query(PlaceCb.filter(F.action == "del_yes"))
async def place_delete_yes(callback: CallbackQuery, callback_data: PlaceCb, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    if not await db.delete_place(user_id, callback_data.place_id):
        await callback.message.edit_text(texts.PLACE_DELETED_ALREADY)
    else:
        await callback.message.edit_text(texts.PLACE_DELETED)
    await show_places(callback.message, user_id, db)


@router.callback_query(PlaceCb.filter(F.action == "del_no"))
async def place_delete_no(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(texts.DELETE_CANCELLED)
