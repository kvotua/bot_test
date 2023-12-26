from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart

from core.utils.dbconnect import Request
from core.keyboards.reply import *
from core.utils.models import *
from core.utils.formsstate import *

import logging


form_router = Router()

@form_router.message(CommandStart())
async def get_start(message: Message, bot: Bot, counter: str, request: Request, state: FSMContext):
    user_is = await request.user_exist(message.from_user.id)

    if user_is == False and isinstance(user_is, bool):
        await request.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'client')

    user:User = await request.get_user(message.from_user.id)

    if user.role == 'admin':
        await message.answer(f'Добро пожаловать в админскую панель, {message.from_user.first_name}!')
        await state.set_state(ProductForm.start)
        await message.answer(f'Выберете дальнейшее действие.', reply_markup=reply_admin)
    else:
        company = await request.user_company_exist(message.from_user.id)
        if company == False and isinstance(company, bool):
            await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно зарегистрировать свое юр. лицо', reply_markup=reply_reg)
        else:
            points = await request.get_all_point_company(message.from_user.id)
            if points == None:
                await state.set_state(OrderForm.add_point)
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно добавить магазин', reply_markup=reply_reg_point_v1)
            else:
                await state.set_state(OrderForm.start)
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин', reply_markup=reply_reg_point_v2)


@form_router.message(OrderForm.start)
async def choose_point(message: Message, request: Request, state: FSMContext):
    if message.text == 'Выбрать торговую точку':
        points = await request.get_all_point_company(message.from_user.id)
        await message.answer(text="Выберете торговую точку",reply_markup=await get_keyboard(points))
        point_id = message.text[0]
        if point_id != 'B':
            await state.update_data(point_id = point_id)
    if message.text == 'Зарегистрировать торговую точку':
        await state.set_state(OrderForm.add_point)
        await message.answer(f'Регистрация')

@form_router.message(OrderForm.add_point)
async def add_point(message: Message, request: Request, state: FSMContext):
    await message.answer(f'Введите город в котором находится магазин')

@form_router.message(ProductForm.start)
async def add_product(message: Message, request: Request, state: FSMContext):
    await state.set_state(ProductForm.add)
    await message.answer(f'Введите название продукта или список продуктов через запятую, которое хотите добавить в бота Ponarth.')

@form_router.message(ProductForm.add)
async def add_product(message: Message, request: Request, state: FSMContext):
    names = message.text.split(",")
    for i in range(len(names)):
        await request.save_poduct(names[i])
        await message.answer(f'{names[i]} - Успешно добавлено')


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def get_cancel(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
