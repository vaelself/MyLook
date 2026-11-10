"""Подбор образа: выбор места и вывод вариантов."""

import random

from aiogram import F, Router
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

import keyboards as kb
import texts
from callbacks import OutfitCb
from outfit import build_outfits
from storage import Storage
from utils import paginate

router = Router()


async def start_outfit(message: Message, user_id: int, db: Storage, page: int = 0,
                       edit: bool = False) -> None:
    """Проверяет, что есть вещи и места, и предлагает выбрать место."""
    if not db.get_items(user_id):
        text, markup = texts.WARDROBE_EMPTY, kb.add_item_kb()
    elif not db.get_places(user_id):
        text, markup = texts.NEED_PLACE_FIRST, kb.add_place_kb()
    else:
        page_places, page, pages = paginate(db.get_places(user_id), page)
        text, markup = texts.ASK_OUTFIT_PLACE, kb.outfit_places_kb(page_places, page, pages)

    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


@router.callback_query(OutfitCb.filter(F.action == "page"))
async def outfit_page(callback: CallbackQuery, callback_data: OutfitCb, db: Storage) -> None:
    await callback.answer()
    await start_outfit(callback.message, callback.from_user.id, db, callback_data.page, edit=True)


@router.callback_query(OutfitCb.filter(F.action.in_({"pick", "again"})))
async def outfit_pick(callback: CallbackQuery, callback_data: OutfitCb, db: Storage) -> None:
    """Пользователь выбрал место (или нажал «Подобрать ещё раз»)."""
    await callback.answer()
    user_id = callback.from_user.id
    message = callback.message

    place = db.get_place(user_id, callback_data.place_id)
    if place is None:
        await message.answer(texts.PLACE_DELETED_ALREADY)
        await start_outfit(message, user_id, db)
        return

    result = build_outfits(db.get_items(user_id), place["id"], random.Random())

    if result.no_items:
        await message.answer(texts.outfit_no_items(place["name"]), reply_markup=kb.outfit_fail_kb())
        return
    if not result.outfits:
        await message.answer(texts.outfit_missing(place["name"], result.missing),
                             reply_markup=kb.outfit_fail_kb())
        return

    for number, outfit in enumerate(result.outfits, start=1):
        # альбом из фото; подпись только у первого фото
        media = []
        for item in outfit:
            caption = texts.outfit_caption(number, place["name"]) if not media else None
            media.append(InputMediaPhoto(media=item["photo_file_id"], caption=caption))
        await message.answer_media_group(media)
        await message.answer(texts.outfit_list(number, outfit))

    final_text = texts.ONLY_ONE_OUTFIT if len(result.outfits) == 1 else texts.WHAT_NEXT
    await message.answer(final_text, reply_markup=kb.outfit_done_kb(place["id"]))
