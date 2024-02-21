from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_label_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Разметить руки")
    kb.button(text="Разметить позу")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
