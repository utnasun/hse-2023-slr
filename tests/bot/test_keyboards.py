import pytest

from slr_bot.keyboards.activity_buttons import get_activity_menu
from slr_bot.keyboards.recognition_buttons import get_label_menu

pytestmark = pytest.mark.parametrize(
    "keyboard,num_buttons,texts,is_resizable",
    [
        (
            get_activity_menu(),
            2,
            [
                "Количество уникальных пользователей",
                "Суммарное количество новых пользователей по дням недели",
            ],
            True,
        ),
        (get_label_menu(), 2, ["Разметить руки", "Разметить позу"], True),
    ],
)


def test_buttons_text(keyboard, num_buttons, texts, is_resizable):
    assert [key.text for key in keyboard.keyboard[0]] == texts


def test_num_buttons(keyboard, num_buttons, texts, is_resizable):
    assert len(keyboard.keyboard[0]) == num_buttons


def test_keyboard_resize(keyboard, num_buttons, texts, is_resizable):
    assert keyboard.resize_keyboard is is_resizable
