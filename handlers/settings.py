"""Настройки: просмотр и изменение города."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts
from callbacks import NavCb
from constants import MAX_CITY
from states import SettingsForm
from storage import Storage
from utils import clean_text

router = Router()


async def show_settings(message: Message, user_id: int, db: Storage) -> None:
    city = db.get_user(user_id)["city"]
    await message.answer(texts.settings_text(city), reply_markup=kb.settings_kb())


@router.callback_query(NavCb.filter(F.action == "edit_city"))
async def edit_city_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(SettingsForm.city)
    await callback.message.answer(texts.ASK_NEW_CITY, reply_markup=kb.cancel_kb())


@router.message(SettingsForm.city, F.text)
async def edit_city(message: Message, state: FSMContext, db: Storage) -> None:
    city = clean_text(message.text, MAX_CITY)
    if city is None:
        await message.answer(texts.bad_length(MAX_CITY))
        return
    await db.set_city(message.from_user.id, city)
    await state.clear()
    await message.answer(texts.city_changed(city), reply_markup=kb.main_menu())
