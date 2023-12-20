from aiogram.fsm.state import StatesGroup, State

class OrderForm(StatesGroup):
    GET_ORDER = State()
    GET_GET_ORDER = State()
    GET_ADRESS = State()
    GET_MONEY = State()