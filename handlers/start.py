"""/start и ввод города при первом запуске."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import keyboards as kb
import texts
from constants import MAX_CITY
from states import StartForm
from storage import Storage
from utils import clean_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Storage) -> None:
    await state.clear()
    user = db.get_user(message.from_user.id)
    if user["city"] is None:
        # первый запуск — спрашиваем город
        await state.set_state(StartForm.city)
        await message.answer(texts.WELCOME + "\n\n" + texts.ASK_CITY,
                             reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(texts.WELCOME_BACK, reply_markup=kb.main_menu())


@router.message(StartForm.city, F.text)
async def first_city(message: Message, state: FSMContext, db: Storage) -> None:
    city = clean_text(message.text, MAX_CITY)
    if city is None:
        await message.answer(texts.bad_length(MAX_CITY))
        return
    await db.set_city(message.from_user.id, city)
    await state.clear()
    await message.answer(texts.CITY_SAVED_FIRST, reply_markup=kb.main_menu())
