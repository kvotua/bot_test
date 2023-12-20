from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.utils.dbconnect import *
from core.utils.orderstate import *

async def get_start_order(message: Message, request: Request, state: FSMContext):
    points = await request.get_all_point_company(message.from_user.id)
    await message.answer(text="Выберете торговую точку",reply_markup=await get_keyboard(points))
    state.set_state(OrderForm.State())
