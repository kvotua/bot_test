import asyncio
import logging
import socket

from aiogram.client.bot import DefaultBotProperties
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardRemove
import asyncpg
import datetime

from core.middlewares.countermiddleware import *
from core.handlers.basic import *
from core.middlewares.countermiddleware import CounterMiddleware
from core.middlewares.dbmiddleware import DbSession
from core.utils.commands import set_commands
from core.utils.formsstate import *
import sheets
from env import db_host, bot_token, user_id_for_push, db_name, db_user, db_pass


async def create_pool():
    return await asyncpg.create_pool(
        host=db_host,
        port=5432,
        database=db_name,
        user=db_user,
        password=db_pass,
        command_timeout=60,
    )


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(
        user_id_for_push,
        text=f"<tg-spoiler>{socket.gethostname()}</tg-spoiler> запустил бота {datetime.now():%Y-%m-%d %H:%M:%S}",
        reply_markup=ReplyKeyboardRemove(),
    )


async def stop_bot(bot: Bot):
    await bot.send_message(
        user_id_for_push,
        text=f"<tg-spoiler>{socket.gethostname()}</tg-spoiler> отключил бота {datetime.now():%Y-%m-%d %H:%M:%S}",
        reply_markup=ReplyKeyboardRemove(),
    )


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - "
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    )

    bot = Bot(bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(rt)

    pool_connect = await create_pool()

    dp.update.middleware.register(DbSession(pool_connect))
    dp.message.middleware.register(CounterMiddleware(pool_connect))

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
