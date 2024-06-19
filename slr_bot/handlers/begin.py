import os
from slr_bot import session

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.dialects.postgresql import insert as pg_insert

from slr_bot.db import bot_users_table, engine
from slr_bot.keyboards.menu import get_main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    # insert_user = (
    #     pg_insert(bot_users_table)
    #     .values(user_id=message.from_user.id)
    #     .on_conflict_do_nothing(index_elements=["user_id"])
    # )

    # with engine.connect() as conn:
    #     conn.execute(insert_user)
    #     conn.commit()

    response = session.get(f'http://{os.environ["APP_HOST"]}/')

    print(response.text)

    await message.answer(
        "Выберите интересующее вас действие", reply_markup=get_main_menu()
    )
