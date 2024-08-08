from aiogram.types import (
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

reply_reg = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Зарегистрироваться")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_reg_point_v1 = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Зарегистрировать торговую точку")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_reg_point_v2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать торговую точку")],
        [
            KeyboardButton(text="Зарегистрировать торговую точку"),
            KeyboardButton(text="Отредактировать торговую точку"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Просмотреть заказы")],
        [KeyboardButton(text="Просмотреть товары")],
        [KeyboardButton(text="Добавить товар")],
        [KeyboardButton(text="Удалить товар")],
        [KeyboardButton(text="Добавить контрагента вручную")],
        [KeyboardButton(text="Добавить на юр. лицо еще одного человека")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_edit_point = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить адрес")],
        [KeyboardButton(text="Изменить название")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_true_info = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Все верно"),
            KeyboardButton(text="Начать заново"),
            KeyboardButton(text="Вернуться в начало"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_true_order = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Все верно"),
            KeyboardButton(text="Начать заново"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_true_point = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Все верно"),
            KeyboardButton(text="Убрать и продолжить"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_true_order_with_comment = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Все верно"),
            KeyboardButton(text="Начать заново"),
        ],
        [
            KeyboardButton(text="Оставить комментарий"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

reply_is_delivery = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Доставка"),
            KeyboardButton(text="Самовывоз"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)
