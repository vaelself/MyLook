"""Все тексты сообщений бота.

Пользовательский текст (названия, категории, город) экранируем через html.escape,
потому что сообщения отправляются с parse_mode=HTML.
"""

from html import escape

from constants import ITEM_TYPES

# ---------- кнопки главного меню ----------
BTN_WARDROBE = "👕 Мой гардероб"
BTN_ADD_ITEM = "➕ Добавить вещь"
BTN_PLACES = "📍 Мои места"
BTN_OUTFIT = "✨ Подобрать образ"
BTN_SHOP = "🛒 Купить одежду"
BTN_SETTINGS = "⚙️ Настройки"
MENU_BUTTONS = [BTN_WARDROBE, BTN_ADD_ITEM, BTN_PLACES, BTN_OUTFIT, BTN_SHOP, BTN_SETTINGS]

# ---------- общие inline-кнопки ----------
BTN_BACK = "⬅️ Назад"
BTN_MAIN_MENU = "🏠 В главное меню"
BTN_CANCEL = "✖️ Отмена"
BTN_DONE = "Готово"
BTN_SKIP = "Пропустить"
BTN_YES_DELETE = "✅ Да, удалить"
BTN_PREV = "◀️"
BTN_NEXT = "▶️"
BTN_TO_LIST = "⬅️ К списку"
BTN_ADD_FIRST_ITEM = "➕ Добавить первую вещь"
BTN_ADD_PLACE = "➕ Добавить место"
BTN_EDIT_NAME = "✏️ Название"
BTN_EDIT_TYPE = "✏️ Тип"
BTN_EDIT_CATEGORY = "✏️ Категория"
BTN_EDIT_PHOTO = "🖼 Фото"
BTN_EDIT_PLACES = "📍 Места"
BTN_DELETE = "🗑 Удалить"
BTN_RENAME = "✏️ Переименовать"
BTN_PLACE_ITEMS = "👕 Вещи для этого места"
BTN_AGAIN = "🔄 Подобрать ещё раз"
BTN_EDIT_CITY = "✏️ Изменить город"

# ---------- общие сообщения ----------
MAIN_MENU = "Главное меню. Выберите действие:"
HELP = (
    "Я помогаю собирать образы из вашей одежды.\n"
    "1. Добавьте вещи через «➕ Добавить вещь» (название, тип, категория, фото).\n"
    "2. Создайте места в «📍 Мои места» (например, «Вуз», «Прогулка») и отметьте подходящие вещи.\n"
    "3. Нажмите «✨ Подобрать образ» и выберите место — я предложу 2 варианта.\n"
    "4. «🛒 Купить одежду» — ссылки на поиск вещи в магазинах.\n"
    "/cancel — отменить текущее действие."
)
CANCELLED = "Действие отменено."
NOTHING_TO_CANCEL = "Сейчас нечего отменять."
UNKNOWN = "Не понимаю это сообщение. Воспользуйтесь кнопками меню или командой /help."
USE_BUTTONS = "Пожалуйста, воспользуйтесь кнопками выше или отправьте /cancel для отмены."
NEED_TEXT = "Пожалуйста, введите текст."
OLD_BUTTON = "Эта кнопка уже неактуальна."
ERROR = "Что-то пошло не так, попробуйте ещё раз."


def bad_length(max_len: int) -> str:
    return f"Длина должна быть от 1 до {max_len} символов. Попробуйте ещё раз:"


# ---------- запуск и город ----------
WELCOME = (
    "Привет! Я бот «Гардероб» 👗\n\n"
    "Я помогу собрать виртуальный гардероб из ваших вещей и подобрать образ "
    "для учёбы, прогулки, ресторана и других мест.\n"
    "Давайте настроим ваш гардероб!"
)
ASK_CITY = "Для начала напишите, в каком городе вы живёте."
NEED_CITY_FIRST = "Сначала нужно указать город. Напишите, в каком городе вы живёте."
CITY_SAVED_FIRST = "Отлично! Теперь давайте наполним ваш гардероб: нажмите «➕ Добавить вещь»."
WELCOME_BACK = "С возвращением!"

# ---------- настройки ----------
ASK_NEW_CITY = "Введите название города:"


def settings_text(city: str | None) -> str:
    return f"Ваш город: {escape(city or 'не указан')}"


def city_changed(city: str) -> str:
    return f"Город изменён: {escape(city)}"


# ---------- добавление вещи ----------
ASK_ITEM_NAME = "Введите название вещи (например, «Чёрная футболка»):"
ASK_ITEM_TYPE = "Выберите тип вещи:"
ASK_CATEGORY = "Введите категорию (например, «Футболка»):"
ASK_PHOTO = "Пришлите фотографию вещи:"
PHOTO_AS_FILE = "Пожалуйста, отправьте изображение как фото, а не как файл."
NEED_PHOTO = "Нужна именно фотография."
ASK_ITEM_PLACES = "Отметьте места, для которых подходит вещь, и нажмите «Готово»:"
NO_PLACES_FOR_ITEM = "У вас пока нет мест. Их можно будет отметить позже в карточке вещи."
ITEM_ADDED = "Вещь добавлена!"

# ---------- гардероб ----------
WARDROBE_EMPTY = "Ваш гардероб пока пуст."
ITEM_DELETED_ALREADY = "Эта вещь уже удалена."
ITEM_DELETED = "Вещь удалена."
DELETE_CANCELLED = "Удаление отменено."
ITEM_UPDATED = "Изменения сохранены."


def wardrobe_page(items: list[dict], page: int, pages: int) -> str:
    """Список вещей на странице, сгруппированный по типу."""
    lines = [f"<b>Ваш гардероб</b> (стр. {page + 1} из {pages}):"]
    current_type = None
    for item in items:
        if item["type"] != current_type:
            current_type = item["type"]
            lines.append(f"\n<b>{ITEM_TYPES[current_type]}</b>")
        lines.append(f"• {escape(item['name'])} ({escape(item['category'])})")
    lines.append("\nНажмите на вещь, чтобы открыть карточку.")
    return "\n".join(lines)


def item_card(item: dict, place_names: list[str]) -> str:
    places = ", ".join(escape(name) for name in place_names) if place_names else "не указаны"
    return (
        f"<b>{escape(item['name'])}</b>\n"
        f"Тип: {ITEM_TYPES[item['type']]}\n"
        f"Категория: {escape(item['category'])}\n"
        f"Места: {places}"
    )


def confirm_delete_item(name: str) -> str:
    return f"Удалить «{escape(name)}»? Это действие нельзя отменить."


# ---------- места ----------
PLACES_EMPTY = "У вас пока нет мест. Добавьте, например, «Вуз», «Прогулка», «Ресторан»."
PLACES_TITLE = "<b>Ваши места:</b>"
ASK_PLACE_NAME = "Введите название места или ситуации (например, «Вуз»):"
PLACE_EXISTS = "Место с таким названием уже есть, введите другое:"
PLACE_ADDED = "Место добавлено."
PLACE_DELETED_ALREADY = "Это место уже удалено."
PLACE_DELETED = "Место удалено."
PLACE_SAVED = "Готово! Изменения сохранены."
ASK_PLACE_ITEMS = "Отметьте вещи для этого места и нажмите «Готово»:"


def ask_items_for_new_place(name: str) -> str:
    return f"Отметьте вещи, которые подходят для «{escape(name)}»:"


def place_card(place: dict, items_count: int) -> str:
    return f"<b>{escape(place['name'])}</b>\nВещей для этого места: {items_count}"


def confirm_delete_place(name: str) -> str:
    return f"Удалить место «{escape(name)}»? Вещи останутся в гардеробе."


# ---------- подбор образа ----------
NEED_PLACE_FIRST = "Сначала создайте место или ситуацию."
ASK_OUTFIT_PLACE = "Куда собираетесь?"
ONLY_ONE_OUTFIT = "Для второго варианта не хватает вещей."
WHAT_NEXT = "Что дальше?"

MISSING_NAMES = {"top": "верха", "bottom": "низа", "shoes": "обуви"}


def outfit_caption(number: int, place_name: str) -> str:
    return f"Вариант {number} для «{escape(place_name)}»:"


def outfit_list(number: int, outfit: list[dict]) -> str:
    names = " + ".join(escape(item["name"]) for item in outfit)
    return f"Вариант {number}: {names}"


def outfit_no_items(place_name: str) -> str:
    return (
        f"Для места «{escape(place_name)}» пока не отмечено ни одной вещи. "
        "Отметьте вещи в карточке места или вещи."
    )


def outfit_missing(place_name: str, missing: list[str]) -> str:
    """Например: «Для места «Вуз» не получается собрать образ: нет обуви.»"""
    parts = []
    clothes = [MISSING_NAMES[t] for t in missing if t in ("top", "bottom")]
    if clothes:
        parts.append("нет " + " и ".join(clothes) + " или цельной вещи (платья, комбинезона)")
    if "shoes" in missing:
        parts.append("нет обуви")
    return f"Для места «{escape(place_name)}» не получается собрать образ: " + "; ".join(parts) + "."


# ---------- покупка ----------
ASK_SHOP_QUERY = "Какую вещь вы хотите найти? Например: «белые кроссовки»."


def shop_result(query: str) -> str:
    return f"Вот где можно поискать «{escape(query)}»:"
