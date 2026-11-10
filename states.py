"""Состояния (FSM) для всех пошаговых диалогов."""

from aiogram.fsm.state import State, StatesGroup


class StartForm(StatesGroup):
    city = State()


class SettingsForm(StatesGroup):
    city = State()


class AddItem(StatesGroup):
    name = State()
    type = State()
    category = State()
    photo = State()
    places = State()


class EditItem(StatesGroup):
    name = State()
    category = State()
    photo = State()
    places = State()


class AddPlace(StatesGroup):
    name = State()
    items = State()


class EditPlace(StatesGroup):
    name = State()
    items = State()


class ShopForm(StatesGroup):
    query = State()


# Состояния, в которых бот ждёт текст (нужно для подсказки в fallback)
TEXT_STATES = {
    StartForm.city.state,
    SettingsForm.city.state,
    AddItem.name.state,
    AddItem.category.state,
    EditItem.name.state,
    EditItem.category.state,
    AddPlace.name.state,
    EditPlace.name.state,
    ShopForm.query.state,
}
