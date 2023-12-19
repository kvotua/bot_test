from aiogram import Bot
from aiogram.types import Message

from core.utils.dbconnect import Request
from core.keyboards.reply import reply_reg
from core.utils.user import *

async def get_start(message: Message, bot: Bot, counter: str, request: Request):
    if not message.from_user.is_bot:
        user_is:bool = await request.is_exist(message.from_user.id)

        if not user_is:
            await request.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'client')

        user:User = await request.get_user(message.from_user.id)

        if user.role == 'admin':
            await message.answer(f'Добро пожаловать в админскую панель, {message.from_user.first_name}!')
        else:
            await message.answer(f'Чтобы сделать заказ заводу Ponarth нужно зарегистрировать свое ИП', reply_markup=reply_reg)

async def get_cancel(message: Message, bot: Bot):
    await message.answer(f'Отчистить все', reply_markup=None)