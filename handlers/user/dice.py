import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from utils.keyboards import play_with_back, back_btn, again_with_back
from utils.functions import edit_message, send_emoji_win
from utils.models import Users
from utils.messages import win_text, lose_text
from utils.states import Play

dice_router = Router()


@dice_router.callback_query(F.data == 'dice')
async def dice_handler(callback: CallbackQuery, state: FSMContext):
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    text = '''🎲 <b>Правила игры в кости:</b>

Бот отправляет в чат два стикера кости. Значения на кубиках выпадают в случайном порядке. <b>Победой в игре считается выпадение "дубля"</b> (двух одинаковых значений, например 6:6). 

Для игры необходимо пополнить баланс и поставить ставку: вы можете воспользоваться как предложенными значениями, так и ввести свою сумму. Сумма ставки снимается с баланса в момент броска.

<b>При выпадении дубля - вы выигрываете</b> и на ваш баланс зачисляются средства равные вашему выигрышу.

🎁 При наличии фриспинов вы можете попытать удачу бесплатно! А если одержите попеду пять раз подряд, то мы зачислим 5000 RUB на ваш баланс.

🔥<b>Коэффициенты на победу:</b>

Если выпадает 2️⃣2️⃣️, ваш выигрыш составляет <b>2 ставки.</b>
Если выпадает 3️⃣3️⃣, ваш выигрыш составляет <b>3 ставки.</b>
Если выпадает 4️⃣4️⃣, ваш выигрыш составляет <b>4 ставки.</b>
Если выпадает 5️⃣5️⃣, ваш выигрыш составляет <b>5 ставок.</b>
Если выпадает 6️⃣6️⃣, ваш выигрыш составляет <b>6 ставок.</b>
Если выпадает 1️⃣1️⃣, ваш выигрыш составляет <b>10 ставок.</b>

<b>👇🏻 Выберите размер ставки из списка или отправьте свою сумму ставки:</b>'''
    if not user.balance and not user.free_balance:
        text += '\n\n⚠️<i><b>Чтобы начать игру, пополните баланс</b></i>'
    else:
        text += '\n\nℹ️ Выберите размер ставки из списка или отправьте свою сумму ставки:'
    await edit_message(callback, text, reply_markup=await play_with_back('play_dice', 'start',
                                                                         user.balance, user.free_balance),
                       parse_mode="HTML")
    await state.set_state(Play.bet_dice)
    await state.update_data(past_msg=callback.message)


@dice_router.callback_query(F.data.split()[0] == 'play_dice')
async def play_dice_handler(callback: CallbackQuery, state: FSMContext):
    bet = int(callback.data.split()[1])
    await handle_playing(callback, state, bet)


@dice_router.message(Play.bet_dice)
async def bet_dice_message(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    if not message.text.isdigit():
        text = '''❌ Ввести можно только цифры
        
ℹ️ Выберите размер ставки из списка или отправьте свою сумму ставки:'''
        await edit_message(data.get('past_msg'), text, reply_markup=await back_btn('dice'))
    bet = int(message.text)
    await handle_playing(message, state, bet)


async def handle_playing(event: CallbackQuery | Message, state: FSMContext, bet: int):
    data = await state.get_data()
    user: Users = Users.get_or_none(Users.user_id == event.from_user.id)
    if not user:
        return await edit_message(data.get('past_msg', event), '❌ Ошибка! Введите /start')
    if (not bet and not user.free_balance) or (bet and user.balance < bet):
        return await edit_message(data.get('past_msg', event), '❌ Ошибка! Пополните баланс',
                                  reply_markup=await back_btn('dice'))
    text = f'🎲 Ваша ставка: {bet}₽\nℹ️ Ваш баланс: {user.balance}₽' if bet else 'ℹ️ Вы использовали бесплатный спин'
    await edit_message(data.get('past_msg', event), text)
    await state.clear()
    if isinstance(event, CallbackQuery):
        a = await event.message.answer_dice()
        b = await event.message.answer_dice()
    else:
        a = await event.answer_dice()
        b = await event.answer_dice()
    if not bet:
        user.free_balance -= 1
    else:
        user.balance -= bet
    await asyncio.sleep(3)
    text = ''
    if a.dice.value == b.dice.value:
        await send_emoji_win(event, a.dice.value)
        if not bet:
            if a.dice.value == 1:
                win_sum = 500 * 10
            else:
                win_sum = 500 * a.dice.value
            text += f'\nЕсли бы ты поставил 500 RUB, ты бы выиграл {win_sum} RUB'
        else:
            if a.dice.value == 1:
                win_sum = bet * 10
            else:
                win_sum = bet * a.dice.value
            user.balance += win_sum
            text += await win_text(bet, win_sum)
    else:
        text += await lose_text()
    user.save()
    if not bet:
        text += f'\n\nℹ️ Бесплатных спинов осталось: {user.free_balance}'
    else:
        text += f'\n\nℹ️ Баланс: {user.balance}₽'
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(text, parse_mode="HTML")
    await message.answer('Выберите действие:', reply_markup=await again_with_back(f'play_dice', bet, 'dice'))
