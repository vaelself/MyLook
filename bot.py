"""Точка входа: запуск Telegram-бота «Гардероб»."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, ErrorEvent
from aiogram.utils.token import TokenValidationError

import texts
from config import BOT_TOKEN, DATA_PATH
from handlers import get_main_router
from storage import Storage

logger = logging.getLogger(__name__)


async def on_error(event: ErrorEvent) -> None:
    """Глобальный обработчик ошибок: пишем в лог и извиняемся перед пользователем."""
    logger.error("Ошибка при обработке апдейта", exc_info=event.exception)
    update = event.update
    try:
        if update.message:
            await update.message.answer(texts.ERROR)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.answer(texts.ERROR)
    except Exception:
        logger.exception("Не удалось отправить сообщение об ошибке")


async def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    if not BOT_TOKEN:
        logger.error("Не задан BOT_TOKEN. Создайте файл .env (см. .env.example).")
        sys.exit(1)
    try:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError:
        logger.error("BOT_TOKEN имеет неверный формат. Проверьте токен от @BotFather.")
        sys.exit(1)

    dp = Dispatcher(storage=MemoryStorage())
    # объект db будет передаваться в хендлеры через аргумент с таким же именем
    dp["db"] = Storage(DATA_PATH)
    dp.include_router(get_main_router())
    dp.errors.register(on_error)

    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск и главное меню"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="cancel", description="Отменить текущее действие"),
    ])

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
