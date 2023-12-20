from aiogram import Bot
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from core.utils.dbconnect import Request
from core.keyboards.reply import *
from core.utils.models import *
from core.utils.orderstate import *

async def get_start(message: Message, bot: Bot, counter: str, request: Request, state: FSMContext):
    if not message.from_user.is_bot:
        user_is = await request.user_exist(message.from_user.id)

        if user_is == False and isinstance(user_is, bool):
            await request.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'client')

        user:User = await request.get_user(message.from_user.id)

        if user.role == 'admin':
            await message.answer(f'Добро пожаловать в админскую панель, {message.from_user.first_name}!')
        else:
            company = await request.user_company_exist(message.from_user.id)
            if company == False and isinstance(company, bool):
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно зарегистрировать свое юр. лицо', reply_markup=reply_reg)
            else:
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин', reply_markup=reply_reg_point_v2)
                await state.set_state(OrderForm.GET_ORDER)


async def get_cancel(message: Message, bot: Bot):
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
    