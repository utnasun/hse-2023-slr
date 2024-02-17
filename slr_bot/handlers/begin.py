from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from slr_bot.keyboards.menu import get_main_menu
from slr_bot.db import engine, bot_users_table
from sqlalchemy.dialects.postgresql import insert as pg_insert


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):

    insert_user = (
        pg_insert(bot_users_table)
        .values(user_id=message.from_user.id)
        .on_conflict_do_nothing(index_elements=['user_id'])
    )

    with engine.connect() as conn:
        conn.execute(insert_user)
        conn.commit()

    await message.answer(
        "Выберите интересующее вас действие",
        reply_markup=get_main_menu()
    )
