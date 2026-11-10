"""«Купить одежду»: ссылки на поиск в магазинах (только по запросу пользователя)."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import keyboards as kb
import texts
from constants import MAX_SHOP_QUERY
from shop import build_shop_links
from states import ShopForm
from utils import clean_text

router = Router()


async def start_shop(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ShopForm.query)
    await message.answer(texts.ASK_SHOP_QUERY, reply_markup=kb.cancel_kb())


@router.message(ShopForm.query, F.text)
async def shop_query(message: Message, state: FSMContext) -> None:
    query = clean_text(message.text, MAX_SHOP_QUERY)
    if query is None:
        await message.answer(texts.bad_length(MAX_SHOP_QUERY))
        return
    await state.clear()
    await message.answer(texts.shop_result(query), reply_markup=kb.shop_kb(build_shop_links(query)))
