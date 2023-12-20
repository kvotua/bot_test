from aiogram.types import KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup

reply_reg = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Зарегистрироваться'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True, selective=True)

reply_reg_point_v1 = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Зарегистрировать торговую точку'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True, selective=True)

reply_reg_point_v2 = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Выбрать торговую точку'
        )
    ],
    [
        KeyboardButton(
            text='Зарегистрировать торговую точку'
        ),
         KeyboardButton(
            text='Отредактировать торговую точку'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True, selective=True)