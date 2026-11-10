"""Всё, что не обработали другие роутеры. Подключается последним."""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import texts
from states import TEXT_STATES

router = Router()


@router.message()
async def unknown_message(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state in TEXT_STATES:
        # ждали текст, а пришло фото/стикер/и т. п.
        await message.answer(texts.NEED_TEXT)
    elif current_state is not None:
        # ждали нажатия на кнопку
        await message.answer(texts.USE_BUTTONS)
    else:
        await message.answer(texts.UNKNOWN, reply_markup=kb.main_menu())


@router.callback_query()
async def unknown_callback(callback: CallbackQuery) -> None:
    # например, кнопка из старого сообщения после /cancel
    await callback.answer(texts.OLD_BUTTON)
