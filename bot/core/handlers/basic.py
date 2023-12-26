from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart

from core.utils.dbconnect import Request
from core.keyboards.reply import *
from core.utils.models import *
from core.utils.orderstate import *


form_router = Router()

@form_router.message(CommandStart())
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
                points = await request.get_all_point_company(message.from_user.id)
                if points == None:
                    await state.set_state(OrderForm.ADD_POINT)
                    await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно добавить магазин', reply_markup=reply_reg_point_v1)
                else:
                    await state.set_state(OrderForm.GET_ORDER)
                    await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин', reply_markup=reply_reg_point_v2)


@form_router.message(OrderForm.GET_ORDER)
async def choose_point(message: Message, request: Request, state: FSMContext):
    points = await request.get_all_point_company(message.from_user.id)
    await message.answer(text="Выберете торговую точку",reply_markup=await get_keyboard(points))
    str = 'по адрессу, '
    start_point_address = find_all_indexes(message.text, str)
    await state.update_data(point = message.text)

@form_router.message(OrderForm.ADD_POINT)
async def add_point(message: Message, request: Request, state: FSMContext):
    await message.answer(f'Введите город в котором находится магазин')

@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def get_cancel(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
