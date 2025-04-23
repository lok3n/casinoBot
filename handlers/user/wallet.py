import datetime
import os

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from utils.functions import edit_message, notify_admins
from utils.models import Users, Payments, Withdraws
from utils.keyboards import wallet_kb, amount_wallet_kb, pay_btn, back_btn, choice_type_withdraw
from utils.states import Wallet
from shop_rukassa import Client, BadRequest

wallet_router = Router()


@wallet_router.callback_query(F.data == 'wallet')
async def wallet_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    if not user:
        return await edit_message(callback, 'Ошибка! Введите /start')
    text = f'''<b>Ваш текущий баланс: <code>{user.balance}</code></b>
    
💰 Вы можете пополнять и выводить баланс без каких-либо ограничений по объему или количеству операций.

<i>ℹ️ Для пополнения баланса воспользуйтесь кнопкой:\n<b>📥 Пополнить</b></i>'''
    await edit_message(callback, text, reply_markup=await wallet_kb(), parse_mode="HTML")


@wallet_router.callback_query(F.data == 'wallet_topup')
async def wallet_topup_handler(callback: CallbackQuery, state: FSMContext):
    await edit_message(callback, 'ℹ️ Выберите сумму для пополнения, или введите её вручную\n'
                                 'Минимальная сумма пополнения 300 RUB',
                       reply_markup=await amount_wallet_kb('topup'))
    await state.set_state(Wallet.topup_choice)


@wallet_router.callback_query(Wallet.topup_choice, F.data.split()[0] == 'topup')
@wallet_router.message(Wallet.topup_choice)
async def topup_choice_handler(event: Message | CallbackQuery, state: FSMContext):
    amount = None
    if isinstance(event, Message):
        if not event.text.isdigit() or int(event.text) < 300:
            return await edit_message(event, '❌ Ошибка! Можно ввести только цифры и сумма должна быть больше 300\n\n'
                                             'ℹ️ Выберите сумму для пополнения, или введите её вручную',
                                      reply_markup=await amount_wallet_kb('topup'))
        amount = int(event.text)
    else:
        amount = int(event.data.split()[1])
    await state.clear()
    client = Client(token=os.getenv('RUKASSA_TOKEN'), shop_id=int(os.getenv('RUKASSA_SHOPID')))
    payment = Payments.create(user_id=event.from_user.id, amount=amount, date_time=datetime.datetime.now())
    client_payment = await client.create_payment(payment.id, amount, user_code=str(event.from_user.id))
    await edit_message(event, f'✅ Вы выбрали сумму для пополнения: <b>{amount}₽</b>\n'
                              f'ℹ️ Оплатите счёт по кнопке ниже, чтобы пополнить баланс',
                       reply_markup=await pay_btn(client_payment.url), parse_mode="HTML")


@wallet_router.callback_query(F.data == 'wallet_withdraw')
async def wallet_withdraw_handler(callback: CallbackQuery, state: FSMContext):
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    await edit_message(callback, 'ℹ️ Выберите сумму для вывода, или введите её вручную\n'
                                 'Минимальная сумма вывода 5000 RUB\n'
                                 f'Текущий баланс: {user.balance} RUB', reply_markup=await back_btn('wallet'))
    await state.set_state(Wallet.withdraw_choice)


@wallet_router.callback_query(Wallet.withdraw_choice, F.data.split()[0] == 'withdraw')
@wallet_router.message(Wallet.withdraw_choice)
async def withdraw_choice_handler(event: Message | CallbackQuery, state: FSMContext):
    amount = None
    if isinstance(event, Message):
        if not event.text.isdigit() or int(event.text) < 5000:
            return await edit_message(event,
                                      '❌ Ошибка! Можно ввести только цифры и сумма должна быть не меньше 5000\n\n'
                                      'ℹ️ Выберите сумму для пополнения, или введите её вручную',
                                      reply_markup=await back_btn('wallet'))
        amount = int(event.text)
    else:
        amount = int(event.data.split()[1])
    user: Users = Users.get_or_none(Users.user_id == event.from_user.id)
    if user.balance < amount:
        return await edit_message(event, '❌ Ошибка! Ваш баланс меньше выбранной суммы, введите сумму меньше\n\n'
                                         'ℹ️ Выберите сумму для пополнения, или введите её вручную',
                                  reply_markup=await back_btn('wallet'))
    await state.update_data(user=user, amount=amount)
    await edit_message(event, f'🤔 Выберите способ выплаты', reply_markup=await choice_type_withdraw(),
                       parse_mode="HTML")


@wallet_router.callback_query(F.data.split()[0] == 'choice_type_wallet')
async def choice_type_wallet_handler(callback: CallbackQuery, state: FSMContext):
    way = callback.data.split()[1]
    mytype = 'телефона' if way == 'SBP' else 'карты'
    await state.update_data(way=way)
    await state.set_state(Wallet.withdraw_wallet)
    await edit_message(callback, f'✍ Введите номер {mytype}, по которому произвести вывод средств:',
                       reply_markup=await back_btn('wallet'), parse_mode="HTML")


@wallet_router.message(Wallet.withdraw_wallet)
async def withdraw_wallet_handler(event: Message, state: FSMContext):
    data = await state.get_data()
    user, amount = data.get('user'), data.get('amount')
    await state.clear()
    client = Client(email=os.getenv('RUKASSA_EMAIL'), password=os.getenv('RUKASSA_PASSWORD'))
    way = data.get('way', 'SBP')
    wallet = event.text
    text = f'''🆕 Запрос на вывод средств 🆕
👤 Пользователь @{event.from_user.username} с ID <code>{event.from_user.id}</code> попытался произвести выплату с баланса <i>[{user.balance}₽]</i>
💵 <b>Сумма:</b> <i>{amount}₽</i>
💳 <b>Способ вывода:</b> <i>{way}</i>
🔢 <b>Номер кошелька:</b> <i>{wallet}</i>'''
    withdraw = Withdraws.create(user_id=event.from_user.id, amount=amount, way=way, wallet=wallet)
    try:
        await client.create_withdraw(way=way, wallet=wallet, amount=amount, order_id=withdraw.id)
    except BadRequest as error:
        withdraw.delete_instance()
        text += f'\n\n❌ Ошибка: {error}'
        await notify_admins(event.bot, text, parse_mode="HTML")
        return await edit_message(event, '❌ Ошибка при создании выплаты, попробуйте ввести другую сумму/номер кошелька',
                                  reply_markup=await back_btn('wallet'))
    user.balance -= amount
    user.save()
    await edit_message(event, f'✅ Вы запросили вывод средств\n'
                              f'Сумма: <b>{amount}₽</b>\n'
                              f'Способ вывода: <b>{way}</b>\n'
                              f'Номер кошелька: <b>{wallet}</b>',
                       reply_markup=await back_btn('wallet'), parse_mode="HTML")
    text += f'\n\n✅ Запрос на вывод передан в платёжную систему'
    await notify_admins(event.bot, text, parse_mode="HTML")
