from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Выберите интересующее вас действие",
        reply_markup=get_main_menu()
    )



