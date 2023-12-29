from aiogram.fsm.state import StatesGroup, State

class OrderForm(StatesGroup):
    start = State()

    add_point = State()
    name = State()
    city = State()
    address = State()

    set_point = State()
    choose_products = State()

class RegLegalEntityForm(StatesGroup):
    start = State()
    kind = State()
    name = State()

class ProductForm(StatesGroup):
    start = State()
    save = State()