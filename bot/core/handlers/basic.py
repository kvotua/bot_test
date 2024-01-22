from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from core.utils.dbconnect import Request
from core.keyboards.reply import *
from core.utils.models import *
from core.utils.formsstate import *
from sheets import Sheet
import logging
import json

rt = Router()

sheet = Sheet()


async def send_message(
    message: Message,
    state: FSMContext,
    request: Request,
    answer: str,
    reply,
    delete=True,
):
    msg = await message.answer(answer, reply_markup=reply)
    message_id = msg.message_id
    await request.save_message(
        message.from_user.id, message_id, answer, delete, "Message bot"
    )


async def send_call(
    call: CallbackQuery,
    state: FSMContext,
    request: Request,
    answer: str,
    reply,
    delete=True,
):
    msg = await call.message.answer(text=answer, reply_markup=reply)
    await request.save_message(
        call.from_user.id, msg.message_id, answer, delete, "Callback"
    )


@rt.message(Command("cancel"))
async def get_cancel(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await send_message(
        message=message,
        state=state,
        request=request,
        answer="Cancelled.",
        reply=ReplyKeyboardRemove(),
    )
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()


@rt.message(CommandStart())
async def get_start(
    message: Message,
    bot: Bot,
    request: Request,
    state: FSMContext,
):
    user_channel_status = await bot.get_chat_member(
        chat_id="ID канала", user_id=message.from_user.id
    )
    if user_channel_status["status"] != "left":
        user_is = await request.user_exist(message.from_user.id)

        if user_is == False and isinstance(user_is, bool):
            await request.add_user(
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name,
                "client",
            )

        user: User = await request.get_user(message.from_user.id)

        if user.role == "admin":
            str = (
                f"Добро пожаловать в админскую панель, {message.from_user.first_name}!"
            )
            await send_message(message, state, request, str, ReplyKeyboardRemove())
            await state.set_state(ProductForm.start)
            await send_message(
                message, state, request, f"Выберете дальнейшее действие.", reply_admin
            )
        else:
            company = await request.user_company_exist(message.from_user.id)
            if company == False and isinstance(company, bool):
                await send_message(
                    message,
                    state,
                    request,
                    f"Чтобы сделать заказ заводу Ponarth, нужно зарегистрировать свое юр. лицо",
                    reply_reg,
                )
                await state.set_state(RegLegalEntityForm.start)
            else:
                points = await request.get_all_point_company(message.from_user.id)
                if points == None:
                    await state.set_state(OrderForm.add_point)
                    await send_message(
                        message,
                        state,
                        request,
                        f"Чтобы сделать заказ заводу Ponarth, нужно добавить магазин",
                        reply_reg_point_v1,
                    )
                else:
                    await state.set_state(OrderForm.start)
                    await send_message(
                        message,
                        state,
                        request,
                        f"Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин",
                        reply_reg_point_v2,
                    )
    else:
        logging.info(
            f"user with id:{message.from_user.id} {message.from_user.username} try to use bot"
        )


#################### reg client ####################


@rt.message(RegLegalEntityForm.start)
async def add_legel_entity(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.set_state(RegLegalEntityForm.kind)
    await state.update_data(user_id=message.text)
    await send_message(
        message,
        state,
        request,
        f"Введите вид юр. лица (ИП, ООО, ...)",
        ReplyKeyboardRemove(),
    )


@rt.message(RegLegalEntityForm.kind)
async def add_legel_entity(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.update_data(kind=message.text)
    await send_message(
        message,
        state,
        request,
        f"Введите название юр. лица (Иван Иванович Иванов, Виктория, ...)",
        ReplyKeyboardRemove(),
    )
    await state.set_state(RegLegalEntityForm.name)


@rt.message(RegLegalEntityForm.name)
async def add_legel_entity(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.update_data(name=message.text)
    await send_message(message, state, request, f"Проверка ...", ReplyKeyboardRemove())
    data = await state.get_data()
    str_temp: str = data["kind"] + " " + data["name"]
    user_id_from_admin = data["user_id"]

    user: User = await request.get_user(message.from_user.id)
    if user.role == "admin":
        await request.add_user(user_id_from_admin, None, None, None, "client")
        await request.add_company(str_temp, user_id_from_admin)
    else:
        await request.add_company(str_temp, message.from_user.id)
    await send_message(
        message,
        state,
        request,
        f"Юр. лицо {str_temp} успешно зарегистрировано!",
        ReplyKeyboardRemove(),
    )
    await state.clear()
    if user.role == "admin":
        await send_message(
            message, state, request, f"Выберете дальнейшее действие.", reply_admin
        )
    else:
        await state.set_state(OrderForm.add_point)
        await send_message(
            message,
            state,
            request,
            f"Чтобы сделать заказ заводу Ponarth, нужно добавить магазин",
            reply_reg_point_v1,
        )


#################### reg client ####################

#################### order ####################


@rt.message(OrderForm.start)
async def point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    if message.text == "Выбрать торговую точку":
        points = await request.get_all_point_company(message.from_user.id)
        await state.update_data(user_id=message.from_user.id)
        await send_message(
            message,
            state,
            request,
            "Выберете торговую точку",
            await get_keyboard(points),
        )
        await state.set_state(OrderForm.choose_products)
    if message.text == "Зарегистрировать торговую точку":
        await state.set_state(OrderForm.city)
        await send_message(
            message,
            state,
            request,
            f"Введите город в котором находится магазин",
            ReplyKeyboardRemove(),
        )


def takePlace(elem):
    return elem.place


@rt.message(OrderForm.choose_products)
async def choose_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    point = message.text.split('"')[1]
    await send_message(
        message,
        state,
        request,
        f"Выбранная торговая точка: {point}",
        ReplyKeyboardRemove(),
    )
    await state.update_data(point=point)
    await state.update_data(products_buf={})
    products = await request.get_products()
    products.sort(key=takePlace)
    kb_products_builder = InlineKeyboardBuilder()
    for i in range(len(products)):
        kb_products_builder.button(
            text=f"{products[i].name}",
            callback_data=ProductButton(product_name=f"{products[i].name}"),
        )
    kb_products_builder.adjust(3)
    kb_products_builder.row(
        InlineKeyboardButton(text=f"Завершить набор", callback_data="End")
    )
    kb_products_builder.row(
        InlineKeyboardButton(text=f"Шаг назад", callback_data="Choose_point")
    )

    await send_message(
        message, state, request, f"Выберете товары", kb_products_builder.as_markup()
    )


@rt.callback_query(F.data == "Choose_point")
async def callback_down(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    request: Request,
):
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    data = await state.get_data()
    data["products_buf"] = {}
    id: int = data["user_id"]
    points = await request.get_all_point_company(id)
    await send_call(
        call, state, request, "Выберете торговую точку", await get_keyboard(points)
    )
    await state.set_state(OrderForm.choose_products)


@rt.callback_query(ProductButton.filter())
async def process_callback_button1(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    request: Request,
):
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    await state.set_state(OrderForm.count)
    product = call.data.split(":")[1].split("_")[0]
    await state.update_data(product_count=product)
    data = await state.get_data()
    products_dict = data["products_buf"]
    products_dict[product] = 0
    await send_call(
        call,
        state,
        request,
        f'Сколько литров "{product}" вы хотите заказать?',
        ReplyKeyboardRemove(),
    )


@rt.message(OrderForm.count)
async def count_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.update_data(count=message.text)
    data = await state.get_data()
    products_dict = data["products_buf"]
    product_count = data["product_count"]
    products_dict[product_count] = message.text
    products = await request.get_products()
    products.sort(key=takePlace)
    kb_products_builder = InlineKeyboardBuilder()
    for i in range(len(products)):
        kb_products_builder.button(
            text=f"{products[i].name}",
            callback_data=ProductButton(product_name=f"{products[i].name}"),
        )
    kb_products_builder.adjust(3)
    kb_products_builder.row(
        InlineKeyboardButton(text=f"Завершить набор", callback_data="End")
    )
    kb_products_builder.row(
        InlineKeyboardButton(text=f"Шаг назад", callback_data="Choose_point")
    )

    await send_message(
        message,
        state,
        request,
        f"Выберете следующую позицию",
        kb_products_builder.as_markup(),
    )


@rt.callback_query(F.data == "End")
async def process_callback_button1(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    request: Request,
):
    await state.set_state(OrderForm.check)
    data = await state.get_data()
    products_dict = data["products_buf"]
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    answer = f"Ваш заказ:\n"
    for key, value in products_dict.items():
        answer += f"{key} - {value} литров \n"
    await state.update_data(bucket=products_dict.copy())
    products_dict.clear()
    await send_call(call, state, request, f"{answer}Все верно?", reply_true_order)


@rt.message(OrderForm.check)
async def check(
    message: Message,
    request: Request,
    state: FSMContext,
):
    answer = message.text
    if answer == "Все верно":
        await state.set_state(OrderForm.choose_date)
        await send_message(
            message, state, request, f"Выберете вид доставки", reply_is_delivery
        )
    if answer == "Отредактировать":
        await state.set_state(OrderForm.edit)
        await send_message(
            message, state, request, f"Надо редактировать", ReplyKeyboardRemove()
        )
        await message.answer(f"Надо редактировать")
    if answer == "Начать заново":
        await state.set_state(OrderForm.choose_products)
        await send_message(
            message, state, request, f"Начать заново", ReplyKeyboardRemove()
        )


@rt.message(OrderForm.choose_date)
async def choose_date(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.update_data(delivery=message.text)
    await state.update_data(user_id=message.from_user.id)
    await send_message(
        message,
        state,
        request,
        f"Выберете день доставки/самовывоза",
        await SimpleCalendar().start_calendar(),
    )


@rt.callback_query(SimpleCalendarCallback.filter())
async def callback_date(
    callback_query: CallbackQuery,
    callback_data: CallbackData,
    state: FSMContext,
    request: Request,
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.set_state(OrderForm.save_order)
        await state.update_data(date_order=date.strftime("%d/%m/%Y"))
        data = await state.get_data()
        bucket = data["bucket"]
        delivery = data["delivery"]
        date_order = data["date_order"]
        point = data["point"]
        user_id = data["user_id"]
        str = f"Вы выбрали \n"
        for key, value in bucket.items():
            str += f"{key}: {value} литров\n"
        str_push = ""
        is_delivery = True
        if delivery == "Доставка на адрес торговой точки":
            str_push = f'{str} По адресу торговой точки "{point}"\n Дата доставки: {date_order}'
        if delivery == "Самовывоз":
            is_delivery = False
            str_push = f"{str} Вид доставки: Самовывоз\n Дата самовывоза: {date_order}\n Торговая точка: {point}"
        await send_call(
            callback_query,
            state,
            request,
            str_push,
            reply_true_order,
        )
        await state.update_data(order_str=str_push)
        point_id = await request.get_point_by_name(user_id, point)
        order_id = await request.create_order(
            user_id, point_id, is_delivery, date_order
        )
        await state.update_data(order_id=order_id)
        logging.info(f"Order id: {order_id}")
        await request.save_bucket_by_order(order_id, bucket)


@rt.message(OrderForm.save_order)
async def choose_date(
    message: Message,
    bot: Bot,
    request: Request,
    state: FSMContext,
):
    await send_message(message, state, request, f"Сохранение...", ReplyKeyboardRemove())
    messages = await request.get_messages_by_user(message.from_user.id)
    for mes in messages:
        if mes["delete"] == True:
            try:
                message_id = mes["message_id"]
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
                await request.delete_message(mes)
            except Exception as e:
                message_id = mes["message_id"]
                # logging.warn(f"Ошибка при удалении сообщения {e}, {message_id}")
    data = await state.get_data()
    order_data = data["order_str"]
    order_id = data["order_id"]
    new_order = order_data.replace("Вы выбрали ", f"Заявка №{order_id}")
    await send_message(message, state, request, new_order, ReplyKeyboardRemove(), False)
    order: Order = await request.get_order(order_id=order_id)
    bucket = await request.get_bucket(order_id=order_id)
    user: User = await request.get_user(order.user_id)
    company_id = await request.user_company_exist(user.user_id)
    company: Company = await request.get_company(company_id=company_id)
    point: Point = await request.get_point(order.point_id)

    date: str = order.date_delivery.strftime("%d-%m-%Y")
    id = sheet.create_week_by_day(datetime.datetime.strptime(date, "%d-%m-%Y"))
    order_info = []
    order_info.append([f"Заявка№{order.id}:", f"{company.legal_entity}"])
    if order.is_delivery == True:
        order_info.append([f"Вид доставки:", f"До адреса торговой точки"])
        order_info.append([f"Адрес:", f"{point.name}"])

    else:
        order_info.append([f"Вид доставки:", f"Самовывоз"])
    order_data = bucket
    date_no_date = datetime.datetime.strptime(date, "%d-%m-%Y")
    sheet.save_order(order_info=order_info, order_data=order_data, date=date_no_date)

    # await send_message(message, state, request, date, ReplyKeyboardRemove())
    await state.clear()


#################### order ####################


@rt.message(OrderForm.add_point)
async def add_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.set_state(OrderForm.city)
    await send_message(
        message,
        state,
        request,
        f"Введите город в котором находится магазин",
        ReplyKeyboardRemove(),
    )


@rt.message(OrderForm.city)
async def city_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.set_state(OrderForm.address)
    await state.update_data(city=message.text)
    await send_message(
        message,
        state,
        request,
        f"Введите адрес в котором находится магазин",
        ReplyKeyboardRemove(),
    )


@rt.message(OrderForm.address)
async def address_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.set_state(OrderForm.name)
    await state.update_data(address=message.text)
    await send_message(
        message,
        state,
        request,
        f"Введите название магазина без кавычек",
        ReplyKeyboardRemove(),
    )


@rt.message(OrderForm.name)
async def name_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.set_state(OrderForm.save)
    await state.update_data(name=message.text)
    data = await state.get_data()
    await send_message(
        message,
        state,
        request,
        f"Проверьте информацию о торговой точке, все верно?",
        ReplyKeyboardRemove(),
    )
    await send_message(
        message,
        state,
        request,
        f'"{data["name"]}" по адресу {data["address"]}, г. {data["city"]}',
        reply_true_info,
    )


@rt.message(OrderForm.save, F.text == "Все верно")
async def save_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    data = await state.get_data()
    await request.add_point(
        data["name"], data["address"], data["city"], message.from_user.id
    )
    await state.clear()
    await state.set_state(OrderForm.start)
    await send_message(
        message,
        state,
        request,
        f"Чтобы сделать заказ заводу Ponarth, нужно выбрать или добавить магазин",
        ReplyKeyboardRemove(),
    )
    await send_message(
        message,
        state,
        request,
        f"Теперь выберете дальнейшее действие",
        reply_reg_point_v2,
    )


@rt.message(OrderForm.save, F.text == "Начать заново")
async def renew_point(
    message: Message,
    request: Request,
    state: FSMContext,
):
    await state.clear()
    await state.set_state(OrderForm.city)
    await send_message(
        message,
        state,
        request,
        f"Введите город в котором находится магазин",
        ReplyKeyboardRemove(),
    )


#################### order ####################

#################### product add ####################


@rt.message(ProductForm.start)
async def add_product(
    message: Message,
    request: Request,
    state: FSMContext,
):
    mes = message.text
    if mes == "Добавить товар":
        await state.set_state(ProductForm.save)
        await send_message(
            message,
            state,
            request,
            f"Введите название продукта или список продуктов и число с указанием места через дефис и через Shift+Enter в общем\n Например: Светлое-4, которое хотите добавить в бота Ponarth.",
            ReplyKeyboardRemove(),
        )
    elif mes == "Просмотреть товары":
        products = await request.get_products()
        products.sort(key=takePlace)
        str = ""
        for i in range(len(products)):
            str += f"- {products[i].name}, позиция - {products[i].place}\n"
        await send_message(
            message,
            state,
            request,
            str,
            ReplyKeyboardRemove(),
        )
        await send_message(message, state, request, f"Конец списка", reply_admin)
    elif mes == "Просмотреть заказы":
        link = sheet.link()
        await send_message(
            message,
            state,
            request,
            f"Ссылка на таблицу - {link}",
            reply_admin,
        )
    elif mes == "Добавить контрагента вручную":
        await state.set_state(RegLegalEntityForm.start)
        await send_message(
            message,
            state,
            request,
            f"Введите user_id",
            ReplyKeyboardRemove(),
        )


@rt.message(ProductForm.save)
async def save_product(
    message: Message,
    request: Request,
    state: FSMContext,
):
    names = message.text.split("\n")
    count = 0
    for i in range(len(names)):
        query_answer = await request.exist_name_product(names[i])
        if query_answer == True:
            await send_message(
                message,
                state,
                request,
                f'Позиция с именем "{names[i]}" уже существует',
                ReplyKeyboardRemove(),
            )
        else:
            if "-" not in names:
                await send_message(
                    message,
                    state,
                    request,
                    f"{names} - введен  не по паттерну",
                    ReplyKeyboardRemove(),
                )
                continue
            product_data = names[i].split("-")
            product_name = product_data[0]
            product_place = product_data[1]
            products = await request.get_products()
            products.sort(key=takePlace)
            logging.info(f"{int(product_place)} - {products[int(product_place)].place}")
            if int(product_place) == products[(int(product_place) - 1)].place:
                for b in range((int(product_place) - 1), (len(products))):
                    await request.change_place(
                        products[b].name, (products[b].place + 1)
                    )
            await request.save_poduct(product_name, product_place)
            await send_message(
                message,
                state,
                request,
                f"{names[i]} - Успешно добавлено",
                ReplyKeyboardRemove(),
            )
            count += 1
    await state.clear()
    await send_message(
        message, state, request, f"Позиций добавлено: {count}", ReplyKeyboardRemove()
    )
    await state.set_state(ProductForm.start)
    await send_message(
        message, state, request, f"Выберете дальнейшее действие.", reply_admin
    )


#################### product add ####################
