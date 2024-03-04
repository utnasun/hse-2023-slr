from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Разметить элементы тела на видео")
    kb.button(text="Распознавание РЖЯ (1 видео)")
    kb.button(text="Оценить бота")
    kb.button(text="Посмотреть рейтинг бота")
    kb.button(text="Получить аналитику об активности")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_rating_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="1", callback_data="num_one"),
            InlineKeyboardButton(text="2", callback_data="num_two"),
            InlineKeyboardButton(text="3", callback_data="num_three"),
            InlineKeyboardButton(text="4", callback_data="num_four"),
            InlineKeyboardButton(text="5", callback_data="num_five")
        ],
        [InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
