"""Общие обработчики: проверка города, /cancel, /help и кнопки главного меню.

Этот роутер подключается первым, поэтому кнопки главного меню срабатывают
в любом состоянии: текущий диалог сбрасывается и открывается нужный раздел.
"""

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

import keyboards as kb
import texts
from callbacks import NavCb
from handlers.outfit import start_outfit
from handlers.places import show_places, start_add_place
from handlers.settings import show_settings
from handlers.shop import start_shop
from handlers.wardrobe import show_wardrobe, start_add_item
from states import StartForm
from storage import Storage

router = Router()


class NeedCity(BaseFilter):
    """Срабатывает, если у пользователя нет города и он прислал что-то кроме /start
    и кроме ответа на вопрос «в каком городе вы живёте»."""

    async def __call__(self, message: Message, db: Storage, state: FSMContext) -> bool:
        if db.get_user(message.from_user.id)["city"] is not None:
            return False
        text = message.text or ""
        if text.startswith("/start"):
            return False
        waiting_city = await state.get_state() == StartForm.city.state
        is_city_answer = waiting_city and text and not text.startswith("/") \
            and text not in texts.MENU_BUTTONS
        return not is_city_answer


# ---------- сначала город ----------

@router.message(NeedCity())
async def ask_city_first(message: Message, state: FSMContext) -> None:
    await state.set_state(StartForm.city)
    await message.answer(texts.NEED_CITY_FIRST, reply_markup=ReplyKeyboardRemove())


# ---------- /cancel и /help ----------

async def cancel_action(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        text = texts.NOTHING_TO_CANCEL
    else:
        text = texts.CANCELLED
    await state.clear()
    await message.answer(text, reply_markup=kb.main_menu())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await cancel_action(message, state)


@router.callback_query(NavCb.filter(F.action == "cancel"))
async def cancel_button(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await cancel_action(callback.message, state)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(texts.HELP, reply_markup=kb.main_menu())


# ---------- кнопки главного меню (работают в любом состоянии) ----------

@router.message(F.text == texts.BTN_WARDROBE)
async def menu_wardrobe(message: Message, state: FSMContext, db: Storage) -> None:
    await state.clear()
    await show_wardrobe(message, message.from_user.id, db)


@router.message(F.text == texts.BTN_ADD_ITEM)
async def menu_add_item(message: Message, state: FSMContext) -> None:
    await start_add_item(message, state)


@router.message(F.text == texts.BTN_PLACES)
async def menu_places(message: Message, state: FSMContext, db: Storage) -> None:
    await state.clear()
    await show_places(message, message.from_user.id, db)


@router.message(F.text == texts.BTN_OUTFIT)
async def menu_outfit(message: Message, state: FSMContext, db: Storage) -> None:
    await state.clear()
    await start_outfit(message, message.from_user.id, db)


@router.message(F.text == texts.BTN_SHOP)
async def menu_shop(message: Message, state: FSMContext) -> None:
    await start_shop(message, state)


@router.message(F.text == texts.BTN_SETTINGS)
async def menu_settings(message: Message, state: FSMContext, db: Storage) -> None:
    await state.clear()
    await show_settings(message, message.from_user.id, db)


# ---------- inline-кнопки навигации ----------

@router.callback_query(NavCb.filter(F.action == "main"))
async def nav_main(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer(texts.MAIN_MENU, reply_markup=kb.main_menu())


@router.callback_query(NavCb.filter(F.action == "add_item"))
async def nav_add_item(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_add_item(callback.message, state)


@router.callback_query(NavCb.filter(F.action == "add_place"))
async def nav_add_place(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_add_place(callback.message, state)


@router.callback_query(NavCb.filter(F.action == "shop"))
async def nav_shop(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_shop(callback.message, state)
