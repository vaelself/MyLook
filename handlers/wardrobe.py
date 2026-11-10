"""Гардероб: добавление вещи, список, карточка, изменение и удаление."""

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts
from callbacks import CheckCb, ItemCb, TypeCb
from constants import ITEM_TYPES, MAX_CATEGORY, MAX_ITEM_NAME
from states import AddItem, EditItem
from storage import Storage
from utils import clean_text, paginate, sorted_items

router = Router()


# ---------- экраны (их вызывают и из других модулей) ----------

async def show_wardrobe(message: Message, user_id: int, db: Storage, page: int = 0,
                        edit: bool = False) -> None:
    """Список вещей. edit=True — изменить текущее сообщение (листание страниц)."""
    items = sorted_items(db.get_items(user_id))
    if not items:
        text, markup = texts.WARDROBE_EMPTY, kb.empty_wardrobe_kb()
    else:
        page_items, page, pages = paginate(items, page)
        text = texts.wardrobe_page(page_items, page, pages)
        markup = kb.wardrobe_kb(page_items, page, pages)

    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def send_item_card(message: Message, user_id: int, db: Storage, item: dict,
                         header: str = "") -> None:
    """Карточка вещи: фото + подпись + кнопки."""
    place_names = [p["name"] for p in db.get_places(user_id) if p["id"] in item["places"]]
    caption = texts.item_card(item, place_names)
    if header:
        caption = header + "\n\n" + caption
    await message.answer_photo(item["photo_file_id"], caption=caption,
                               reply_markup=kb.item_card_kb(item["id"]))


async def start_add_item(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddItem.name)
    await message.answer(texts.ASK_ITEM_NAME, reply_markup=kb.cancel_kb())


def place_options(db: Storage, user_id: int) -> list[tuple[int, str]]:
    """Места в виде (id, название) для мультивыбора."""
    return [(p["id"], p["name"]) for p in db.get_places(user_id)]


async def item_not_found(message: Message, user_id: int, db: Storage) -> None:
    await message.answer(texts.ITEM_DELETED_ALREADY)
    await show_wardrobe(message, user_id, db)


# ---------- добавление вещи: шаг 1 — название ----------

@router.message(AddItem.name, F.text)
async def add_item_name(message: Message, state: FSMContext) -> None:
    name = clean_text(message.text, MAX_ITEM_NAME)
    if name is None:
        await message.answer(texts.bad_length(MAX_ITEM_NAME))
        return
    await state.update_data(name=name)
    await state.set_state(AddItem.type)
    await message.answer(texts.ASK_ITEM_TYPE, reply_markup=kb.types_kb())


# ---------- шаг 2 — тип ----------

@router.callback_query(AddItem.type, TypeCb.filter(F.item_id == 0))
async def add_item_type(callback: CallbackQuery, callback_data: TypeCb, state: FSMContext) -> None:
    await callback.answer()
    if callback_data.code not in ITEM_TYPES:
        return
    await state.update_data(type=callback_data.code)
    await state.set_state(AddItem.category)
    await callback.message.edit_reply_markup(reply_markup=None)  # убираем кнопки типов
    await callback.message.answer(texts.ASK_CATEGORY, reply_markup=kb.cancel_kb())


# ---------- шаг 3 — категория ----------

@router.message(AddItem.category, F.text)
async def add_item_category(message: Message, state: FSMContext) -> None:
    category = clean_text(message.text, MAX_CATEGORY)
    if category is None:
        await message.answer(texts.bad_length(MAX_CATEGORY))
        return
    await state.update_data(category=category)
    await state.set_state(AddItem.photo)
    await message.answer(texts.ASK_PHOTO, reply_markup=kb.cancel_kb())


# ---------- шаг 4 — фото ----------

@router.message(AddItem.photo, F.photo)
async def add_item_photo(message: Message, state: FSMContext, db: Storage) -> None:
    # берём самый большой размер фото
    await state.update_data(photo=message.photo[-1].file_id, selected=[])
    await state.set_state(AddItem.places)

    options = place_options(db, message.from_user.id)
    text = texts.ASK_ITEM_PLACES if options else texts.NO_PLACES_FOR_ITEM
    await message.answer(text, reply_markup=kb.multiselect_kb(options, [], 0))


@router.message(StateFilter(AddItem.photo, EditItem.photo), ~F.photo)
async def not_a_photo(message: Message) -> None:
    """Пришло не фото: остаёмся на шаге и подсказываем."""
    document = message.document
    if document and document.mime_type and document.mime_type.startswith("image/"):
        await message.answer(texts.PHOTO_AS_FILE)
    else:
        await message.answer(texts.NEED_PHOTO)


# ---------- шаг 5 — места (мультивыбор) ----------

@router.callback_query(StateFilter(AddItem.places, EditItem.places),
                       CheckCb.filter(F.action.in_({"toggle", "page"})))
async def item_places_toggle(callback: CallbackQuery, callback_data: CheckCb,
                             state: FSMContext, db: Storage) -> None:
    """Отметить/снять место или перелистнуть страницу."""
    await callback.answer()
    data = await state.get_data()
    selected = data["selected"]
    if callback_data.action == "toggle":
        if callback_data.id in selected:
            selected.remove(callback_data.id)
        else:
            selected.append(callback_data.id)
        await state.update_data(selected=selected)

    options = place_options(db, callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=kb.multiselect_kb(options, selected, callback_data.page))


@router.callback_query(AddItem.places, CheckCb.filter(F.action == "done"))
async def add_item_done(callback: CallbackQuery, state: FSMContext, db: Storage) -> None:
    """Сохраняем новую вещь."""
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    await state.clear()

    # на всякий случай убираем места, которые успели удалить
    existing = {place_id for place_id, _ in place_options(db, user_id)}
    places = [place_id for place_id in data["selected"] if place_id in existing]

    item = await db.add_item(user_id, data["name"], data["type"], data["category"],
                             data["photo"], places)
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_item_card(callback.message, user_id, db, item, texts.ITEM_ADDED)
    await callback.message.answer(texts.MAIN_MENU, reply_markup=kb.main_menu())


# ---------- список и карточка ----------

@router.callback_query(ItemCb.filter(F.action == "list"))
async def item_list(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    await show_wardrobe(callback.message, callback.from_user.id, db, callback_data.page)


@router.callback_query(ItemCb.filter(F.action == "page"))
async def item_list_page(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    await show_wardrobe(callback.message, callback.from_user.id, db, callback_data.page, edit=True)


@router.callback_query(ItemCb.filter(F.action == "open"))
async def item_open(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    item = db.get_item(user_id, callback_data.item_id)
    if item is None:
        await item_not_found(callback.message, user_id, db)
        return
    await send_item_card(callback.message, user_id, db, item)


# ---------- изменение полей ----------

# какое действие кнопки -> какое состояние и какой вопрос
EDIT_FIELDS = {
    "name": (EditItem.name, texts.ASK_ITEM_NAME),
    "cat": (EditItem.category, texts.ASK_CATEGORY),
    "photo": (EditItem.photo, texts.ASK_PHOTO),
}


@router.callback_query(ItemCb.filter(F.action.in_(EDIT_FIELDS)))
async def item_edit_start(callback: CallbackQuery, callback_data: ItemCb,
                          state: FSMContext, db: Storage) -> None:
    """Начало изменения названия, категории или фото."""
    await callback.answer()
    if db.get_item(callback.from_user.id, callback_data.item_id) is None:
        await item_not_found(callback.message, callback.from_user.id, db)
        return
    new_state, question = EDIT_FIELDS[callback_data.action]
    await state.clear()
    await state.set_state(new_state)
    await state.update_data(item_id=callback_data.item_id)
    await callback.message.answer(question, reply_markup=kb.cancel_kb())


async def save_item_field(message: Message, state: FSMContext, db: Storage,
                          field: str, value) -> None:
    """Сохраняет поле вещи и показывает обновлённую карточку."""
    user_id = message.from_user.id
    data = await state.get_data()
    await state.clear()
    if not await db.update_item(user_id, data["item_id"], field, value):
        await item_not_found(message, user_id, db)
        return
    item = db.get_item(user_id, data["item_id"])
    await send_item_card(message, user_id, db, item, texts.ITEM_UPDATED)


@router.message(EditItem.name, F.text)
async def item_edit_name(message: Message, state: FSMContext, db: Storage) -> None:
    name = clean_text(message.text, MAX_ITEM_NAME)
    if name is None:
        await message.answer(texts.bad_length(MAX_ITEM_NAME))
        return
    await save_item_field(message, state, db, "name", name)


@router.message(EditItem.category, F.text)
async def item_edit_category(message: Message, state: FSMContext, db: Storage) -> None:
    category = clean_text(message.text, MAX_CATEGORY)
    if category is None:
        await message.answer(texts.bad_length(MAX_CATEGORY))
        return
    await save_item_field(message, state, db, "category", category)


@router.message(EditItem.photo, F.photo)
async def item_edit_photo(message: Message, state: FSMContext, db: Storage) -> None:
    await save_item_field(message, state, db, "photo_file_id", message.photo[-1].file_id)


@router.callback_query(ItemCb.filter(F.action == "type"))
async def item_edit_type_start(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    if db.get_item(callback.from_user.id, callback_data.item_id) is None:
        await item_not_found(callback.message, callback.from_user.id, db)
        return
    await callback.message.answer(texts.ASK_ITEM_TYPE,
                                  reply_markup=kb.types_kb(callback_data.item_id))


@router.callback_query(TypeCb.filter(F.item_id != 0))
async def item_edit_type(callback: CallbackQuery, callback_data: TypeCb, db: Storage) -> None:
    await callback.answer()
    if callback_data.code not in ITEM_TYPES:
        return
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    if not await db.update_item(user_id, callback_data.item_id, "type", callback_data.code):
        await item_not_found(callback.message, user_id, db)
        return
    item = db.get_item(user_id, callback_data.item_id)
    await send_item_card(callback.message, user_id, db, item, texts.ITEM_UPDATED)


@router.callback_query(ItemCb.filter(F.action == "places"))
async def item_edit_places_start(callback: CallbackQuery, callback_data: ItemCb,
                                 state: FSMContext, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    item = db.get_item(user_id, callback_data.item_id)
    if item is None:
        await item_not_found(callback.message, user_id, db)
        return

    options = place_options(db, user_id)
    if not options:
        await callback.message.answer(texts.PLACES_EMPTY, reply_markup=kb.add_place_kb())
        return

    await state.clear()
    await state.set_state(EditItem.places)
    await state.update_data(item_id=item["id"], selected=list(item["places"]))
    await callback.message.answer(texts.ASK_ITEM_PLACES,
                                  reply_markup=kb.multiselect_kb(options, item["places"], 0))


@router.callback_query(EditItem.places, CheckCb.filter(F.action == "done"))
async def item_edit_places_done(callback: CallbackQuery, state: FSMContext, db: Storage) -> None:
    await callback.answer()
    # callback.message — это сообщение бота, поэтому user_id берём из callback
    user_id = callback.from_user.id
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    existing = {place_id for place_id, _ in place_options(db, user_id)}
    places = [place_id for place_id in data["selected"] if place_id in existing]
    if not await db.set_item_places(user_id, data["item_id"], places):
        await item_not_found(callback.message, user_id, db)
        return
    item = db.get_item(user_id, data["item_id"])
    await send_item_card(callback.message, user_id, db, item, texts.ITEM_UPDATED)


# ---------- удаление ----------

@router.callback_query(ItemCb.filter(F.action == "del"))
async def item_delete_ask(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    item = db.get_item(callback.from_user.id, callback_data.item_id)
    if item is None:
        await item_not_found(callback.message, callback.from_user.id, db)
        return
    await callback.message.answer(
        texts.confirm_delete_item(item["name"]),
        reply_markup=kb.confirm_kb(ItemCb(action="del_yes", item_id=item["id"]),
                                   ItemCb(action="del_no", item_id=item["id"])))


@router.callback_query(ItemCb.filter(F.action == "del_yes"))
async def item_delete_yes(callback: CallbackQuery, callback_data: ItemCb, db: Storage) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    if not await db.delete_item(user_id, callback_data.item_id):
        await callback.message.edit_text(texts.ITEM_DELETED_ALREADY)
    else:
        await callback.message.edit_text(texts.ITEM_DELETED)
    await show_wardrobe(callback.message, user_id, db)


@router.callback_query(ItemCb.filter(F.action == "del_no"))
async def item_delete_no(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(texts.DELETE_CANCELLED)
