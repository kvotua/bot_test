from aiogram.fsm.state import StatesGroup, State

class OrderForm(StatesGroup):
    start = State()
    add_point = State()
    set_point = State()


class ProductForm(StatesGroup):
    start = State()
    add = State()