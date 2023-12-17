import os
from datetime import datetime, date
from dotenv import load_dotenv
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

load_dotenv(dotenv_path='.env')

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')

bot = Bot(bot_token)
dp = Dispatcher()

@dp.message(commands=['start','welocme','about'])
async def cmd_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!"), message.answer_sticker('CAACAgIAAxkBAAEoNxBleGTk8ZnvZwO7H7mvCP5AaWs89gACwRgAAn2IqUiOzhz_SUBYkDME')

@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main() -> None:
    bot = Bot(bot_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())