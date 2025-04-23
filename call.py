from typing import Dict
from fastapi import FastAPI, Request, status
from main import bot
from utils.models import Users, Payments, Withdraws
from utils.functions import notify_admins
from utils.keyboards import back_btn
from shop_rukassa import Payment
import logging

app = FastAPI()


def serialization(data_str: str) -> Dict:
    data = {}
    for i in data_str.split("&"):
        key, value = i.split("=")
        data[key] = value
    return data


@app.post("/payment")
async def root(request: Request):
    body = await request.body()
    data = serialization(body.decode("utf-8"))
    logging.info(f'NEW PAYMENT - {data}')
    client_payment = Payment(**data)
    if client_payment.way:
        return await withdraw_handle(client_payment)
    else:
        return await order_handle(client_payment)


async def order_handle(client_payment: Payment):
    try:
        payment: Payments = Payments.get_by_id(int(client_payment.order_id))
    except Exception as e:
        await notify_admins(bot, f'❌ Пришел неопознанный платеж под номером #{client_payment.order_id}\n'
                                 f'Сумма: {client_payment.amount}₽\n'
                                 f'error: {e}')
        return status.HTTP_400_BAD_REQUEST
    if float(payment.amount) != float(client_payment.amount):
        await notify_admins(bot, f'❌ Пришел опознанный платеж под номером #{client_payment.order_id} с другой суммой\n'
                                 f'Сумма: {payment.amount}₽\n'
                                 f'Сумма списания: {client_payment.amount}₽\n')
        return status.HTTP_400_BAD_REQUEST
    if not payment.finished:
        user: Users = Users.get_or_none(user_id=payment.user_id)
        if not user:
            return status.HTTP_400_BAD_REQUEST
        user.balance += int(payment.amount)
        payment.finished = 1
        payment.save()
        user.save()
        await bot.send_message(payment.user_id, f'✅ Вы успешно пополнили баланс на сумму {payment.amount}₽',
                               reply_markup=await back_btn('start'))

    return status.HTTP_200_OK


async def withdraw_handle(client_payment: Payment):
    try:
        withdraw: Withdraws = Withdraws.get_by_id(int(client_payment.order_id))
    except Exception as e:
        await notify_admins(bot, f'❌ Пришло неопознанное подтверждение оплаты #{client_payment.order_id}\n'
                                 f'Сумма: {client_payment.amount}₽\n'
                                 f'error: {e}')
        return status.HTTP_400_BAD_REQUEST
    if not withdraw.finished:
        withdraw.finished = 1
        withdraw.save()
        await bot.send_message(withdraw.user_id, f'✅ Ваша заявка на вывод средств выполнена\n'
                                                 f'Сумма: {client_payment.amount}\n'
                                                 f'Способ выплаты: {client_payment.way}',
                               reply_markup=await back_btn('start'))
    return status.HTTP_200_OK
