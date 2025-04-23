from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from utils.keyboards import main_menu
from utils.models import Users
from utils.functions import edit_message, is_admin

start_router = Router()


@start_router.message(Command('start'))
@start_router.callback_query(F.data == 'start')
async def start_handler(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    user: Users = Users.get_or_create(user_id=event.from_user.id)[0]
    text = f'''👋 <b>Привет, {event.from_user.first_name}!</b>

Добро пожаловать в DICE JET! Здесь ты сможешь поиграть в популярную игру кости.

Для ставок используется твой внутренний баланс. Всё абсолютно честно и прозрачно, механика игр описана в разделе <b>«💯 Гарантии»</b> 
Пополнить баланс можно в разделе <b>«Баланс»</b> 

Для взаимодействия с ботом используй кнопки ниже 👇'''
    await edit_message(event, text, reply_markup=await main_menu(await is_admin(event.from_user.id)), parse_mode="HTML")
    if user.free_balance == 5 and isinstance(event, Message):
        await event.answer('''Мы дарим тебе 5 приветственных спинов. С их помощью ты сможешь разобарться как устроена игра. 

Если ты выбьешь 5 дублей подряд, то мы начислим на баланс 5000 руб, которые ты сможешь преумножить или вывести. 

Жми кнопку «Играть» - попытай свою удачу!''')
