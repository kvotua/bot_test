from aiogram.fsm.state import StatesGroup, State

class OrderForm(StatesGroup):
    GET_ORDER = State()
    ADD_POINT = State ()
    GET_ADRESS = State()
    GET_MONEY = State()
    SET_ADD_POINT = State()