"""Сборка всех роутеров. Порядок важен: common первым, fallback последним."""

from aiogram import Router

from handlers import common, fallback, outfit, places, settings, shop, start, wardrobe


def get_main_router() -> Router:
    router = Router()
    router.include_routers(
        common.router,
        start.router,
        wardrobe.router,
        places.router,
        outfit.router,
        shop.router,
        settings.router,
        fallback.router,  # обязательно последним
    )
    return router
