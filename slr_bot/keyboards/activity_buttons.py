from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_activity_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Количество уникальных пользователей")
    kb.button(text="Суммарное количество новых пользователей по дням недели")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
