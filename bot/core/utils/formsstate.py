from aiogram.fsm.state import StatesGroup, State

class OrderForm(StatesGroup):
    start = State()

    add_point = State()
    name = State()
    city = State()
    address = State()
    save = State()

    set_point = State()
    choose_products = State()
    count = State()

    check = State()
    choose_date = State()
    edit = State()
    save_order = State()

class RegLegalEntityForm(StatesGroup):
    start = State()
    kind = State()
    name = State()

class ProductForm(StatesGroup):
    start = State()
    save = State()