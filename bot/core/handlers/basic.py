from aiogram import Bot
from aiogram.types import Message

from core.utils.dbconnect import Request
from core.keyboards.reply import reply_reg

async def get_start(message: Message, bot: Bot, counter: str, request: Request):
    if not message.from_user.is_bot:
        user = await request.get_user(message.from_user.id)
        await message.answer(user.__str__())
        await message.answer(str(message.from_user.id))
        await message.answer(f'Чтобы сделать заказ заводу Ponarth нужно зарегистрировать свое ИП', reply_markup=reply_reg)

async def get_cancel(message: Message, bot: Bot):
    await message.answer(reply_markup=None)