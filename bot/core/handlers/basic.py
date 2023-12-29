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
            await state.set_state(RegLegalEntityForm.start)
        else:
            points = await request.get_all_point_company(message.from_user.id)
            if points == None:
                await state.set_state(OrderForm.add_point)
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно добавить магазин', reply_markup=reply_reg_point_v1)
            else:
                await state.set_state(OrderForm.start)
                await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин', reply_markup=reply_reg_point_v2)

#################### reg client ####################

@form_router.message(RegLegalEntityForm.start)
async def add_legel_entity(message: Message, request: Request, state: FSMContext):
    await state.set_state(RegLegalEntityForm.kind)
    await message.answer(f'Введите вид юр. лица (ИП, ООО, ...)')

@form_router.message(RegLegalEntityForm.kind)
async def add_legel_entity(message: Message, request: Request, state: FSMContext):
    await state.update_data(kind=message.text)    
    await message.answer(f'Введите название Вашего юр. лица (Иван Иванович Иванов, Виктория, ...)')
    await state.set_state(RegLegalEntityForm.name)

@form_router.message(RegLegalEntityForm.name)
async def add_legel_entity(message: Message, request: Request, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(f'Проверка ...')
    data = await state.get_data()
    str_temp:str = data["kind"] + " " + data["name"]

    await request.add_company(str_temp, message.from_user.id)
    await message.answer(f'Ваше юр. лицо {str_temp} успешно зарегистрировано!')
    await state.clear()
    await state.set_state(OrderForm.add_point)
    await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно добавить магазин', reply_markup=reply_reg_point_v1)

#################### reg client ####################

#################### order ####################

@form_router.message(OrderForm.start)
async def choose_point(message: Message, request: Request, state: FSMContext):
    if message.text == 'Выбрать торговую точку':
        points = await request.get_all_point_company(message.from_user.id)
        await message.answer(text="Выберете торговую точку",reply_markup=await get_keyboard(points))
        await state.set_state(OrderForm.choose_products)
    if message.text == 'Зарегистрировать торговую точку':
        await state.set_state(OrderForm.add_point)
        await message.answer(f'Регистрация')

@form_router.message(OrderForm.choose_products)
async def add_point(message: Message, request: Request, state: FSMContext):
    point_id = message.text[0]
    await state.update_data(point_id = point_id)
    await message.answer(f'Выберете товары')

@form_router.message(OrderForm.add_point)
async def add_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.city)
    await message.answer(f'Введите город в котором находится магазин')

@form_router.message(OrderForm.city)
async def add_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.address)
    await state.update_data(city=message.text)
    await message.answer(f'Введите адрес в котором находится магазин')    

@form_router.message(OrderForm.address)
async def add_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.name)
    await state.update_data(address=message.text)
    await message.answer(f'Введите название магазина')  

@form_router.message(OrderForm.name)
async def add_point(message: Message, request: Request, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await request.add_point(data["name"], data["address"], data["city"],  message.from_user.id)
    await state.clear()
    await state.set_state(OrderForm.start)
    await message.answer(f'Теперь выберете дальнейшее действие', reply_markup=reply_reg_point_v2)

#################### order ####################

#################### product add ####################

@form_router.message(ProductForm.start)
async def add_product(message: Message, request: Request, state: FSMContext):
    mes = message.text
    if mes == "Добавить товар":
            await state.set_state(ProductForm.save)
            await message.answer(f'Введите название продукта или список продуктов через Shift+Enter, которое хотите добавить в бота Ponarth.')
    elif mes =='Просмотреть товары':
            products = await request.get_products()
            for i in range(len(products)):
                await message.answer(f'- {products[i]}') 
                await message.answer(f'Конец списка', reply_markup=reply_admin)
    elif mes =='Просмотреть заказы':
            await message.answer(f'Заказов нет', reply_markup=reply_admin)


@form_router.message(ProductForm.save)
async def add_product(message: Message, request: Request, state: FSMContext):
    names = message.text.split("\n")
    for i in range(len(names)):
        await request.save_poduct(names[i])
        await message.answer(f'{names[i]} - Успешно добавлено')
    await state.clear()

#################### product add ####################

@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def get_cancel(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
