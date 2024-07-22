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

    edit_point = State()
    edit_point_category = State()
    save_edit = State()

    check_point = State()
    save_comment = State()

    count = State()

    check = State()
    choose_date = State()
    edit = State()
    save_order = State()


class RegLegalEntityForm(StatesGroup):
    start = State()
    kind = State()
    name = State()
    startStuff = State()
    chooseStuffOrPartner = State()
    chooseStuffPoint = State()
    save = State()


class ProductForm(StatesGroup):
    start = State()
    choose_place = State()
    edit = State()
    edit = State()
    get_orders = State()
    save = State()
