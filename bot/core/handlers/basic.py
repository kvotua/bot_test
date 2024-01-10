from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.utils.dbconnect import Request
from core.keyboards.reply import *
from core.utils.models import *
from core.utils.formsstate import *

import logging

rt = Router()

@rt.message(Command("cancel"))
async def get_cancel(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()

@rt.message(CommandStart())
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

@rt.message(RegLegalEntityForm.start)
async def add_legel_entity(message: Message, request: Request, state: FSMContext):
    await state.set_state(RegLegalEntityForm.kind)
    await message.answer(f'Введите вид юр. лица (ИП, ООО, ...)')

@rt.message(RegLegalEntityForm.kind)
async def add_legel_entity(message: Message, request: Request, state: FSMContext):
    await state.update_data(kind=message.text)    
    await message.answer(f'Введите название Вашего юр. лица (Иван Иванович Иванов, Виктория, ...)')
    await state.set_state(RegLegalEntityForm.name)

@rt.message(RegLegalEntityForm.name)
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

@rt.message(OrderForm.start)
async def point(message: Message, request: Request, state: FSMContext):
    if message.text == 'Выбрать торговую точку':
        points = await request.get_all_point_company(message.from_user.id)
        await message.answer(text="Выберете торговую точку",reply_markup=await get_keyboard(points))
        await state.set_state(OrderForm.choose_products)
    if message.text == 'Зарегистрировать торговую точку':
        await state.set_state(OrderForm.city)
        await message.answer(f'Введите город в котором находится магазин')

@rt.message(OrderForm.choose_products)
async def choose_point(message: Message, request: Request, state: FSMContext):
    point = message.text.split('"')[1]
    await message.answer(f'Выбранная торговая точка: {point}')
    await state.update_data(point = point)
    products = await request.get_products()
    kb_products_builder = InlineKeyboardBuilder()
    for i in range(len(products)):
        kb_products_builder.button(text= f'{products[i]}', callback_data=ProductButton(product_name=f'{products[i]}'))
    kb_products_builder.button(text= f'Завершить набор', callback_data='End')
    kb_products_builder.adjust(3)
    
    await message.answer(text=f'Выберете товары', reply_markup=kb_products_builder.as_markup())


products_dict = {}

@rt.callback_query(ProductButton.filter())
async def process_callback_button1(call: CallbackQuery, bot: Bot,  state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await state.set_state(OrderForm.count)
    product = call.data.split(':')[1].split('_')[0]
    await state.update_data(product_count = product)
    products_dict[product] = 0
    await call.message.answer(f'Сколько кег "{product}" вы хотите заказать?')
    # if products_dict.get(product) == None:
    #     products_dict[product] = 0

@rt.message(OrderForm.count)
async def count_point(message: Message, request: Request, state: FSMContext):
    await state.update_data(count = message.text)
    data = await state.get_data()
    product_count = data["product_count"]
    products_dict[product_count] = message.text
    products = await request.get_products()
    kb_products_builder = InlineKeyboardBuilder()
    for i in range(len(products)):
        kb_products_builder.button(text= f'{products[i]}', callback_data=ProductButton(product_name=f'{products[i]}'))
    kb_products_builder.button(text= f'Завершить набор', callback_data='End')
    kb_products_builder.adjust(3)
    await message.answer(f'Выберете следующую позицию', reply_markup=kb_products_builder.as_markup())

@rt.callback_query(F.data == 'End')
async def process_callback_button1(call: CallbackQuery, bot: Bot,  state: FSMContext, request: Request):
    await state.set_state(OrderForm.check)
    
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(f'Ваш заказ:')
    for key, value in products_dict.items():
        await call.message.answer(f'{key} - {value} кег \n')
    pr = products_dict
    products_dict.clear()
    await call.message.answer(f'Все верно?', reply_markup=reply_true_order)
    
@rt.message(OrderForm.check)
async def check(message: Message, request: Request, state: FSMContext):
    answer = message.text
    if answer == 'Все верно':
        await state.set_state(OrderForm.save)
        await message.answer(f'Верно')
    if answer == 'Отредактировать':
        await state.set_state(OrderForm.edit)
        await message.answer(f'Надо редактировать')
    if answer == "Начать заново":
        await state.set_state(OrderForm.choose_products)
        await message.answer(f'Начать заново')

#################### order ####################

@rt.message(OrderForm.add_point)
async def add_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.city)
    await message.answer(f'Введите город в котором находится магазин')

@rt.message(OrderForm.city)
async def city_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.address)
    await state.update_data(city=message.text)
    await message.answer(f'Введите адрес в котором находится магазин')    

@rt.message(OrderForm.address)
async def address_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.name)
    await state.update_data(address=message.text)
    await message.answer(f'Введите название магазина без кавычек')  

@rt.message(OrderForm.name)
async def name_point(message: Message, request: Request, state: FSMContext):
    await state.set_state(OrderForm.save)
    await state.update_data(name=message.text)
    data = await state.get_data()
    await message.answer(f'Проверьте информацию о торговой точке, все верно?')
    await message.answer(f'"{data["name"]}" по адресу {data["address"]}, г. {data["city"]}', reply_markup=reply_true_info)

@rt.message(OrderForm.save, F.text =='Все верно')
async def save_point(message: Message, request: Request, state: FSMContext):
    data = await state.get_data()
    await request.add_point(data["name"], data["address"], data["city"],  message.from_user.id)
    await state.clear()
    await state.set_state(OrderForm.start)
    await message.answer(f'Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин')
    await message.answer(f'Теперь выберете дальнейшее действие', reply_markup=reply_reg_point_v2)

@rt.message(OrderForm.save, F.text =="Начать заново")
async def renew_point(message: Message, request: Request, state: FSMContext):
    await state.clear()
    await state.set_state(OrderForm.city)
    await message.answer(f'Введите город в котором находится магазин')

#################### order ####################

#################### product add ####################

@rt.message(ProductForm.start)
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


@rt.message(ProductForm.save)
async def save_product(message: Message, request: Request, state: FSMContext):
    names = message.text.split("\n")
    count = 0
    for i in range(len(names)):
        query_answer = await request.exist_name_product(names[i])
        if query_answer == True:
            await message.answer(f'Позиция с именем "{names[i]}" уже существует')
        else:
            await request.save_poduct(names[i])
            await message.answer(f'{names[i]} - Успешно добавлено')
            count += 1
    await state.clear()
    await message.answer(f'Позиций добавлено: {count}', )
    await state.set_state(ProductForm.start)
    await message.answer(f'Выберете дальнейшее действие.', reply_markup=reply_admin)


#################### product add ####################