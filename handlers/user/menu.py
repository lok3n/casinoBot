import os

from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.functions import edit_message
from utils.keyboards import back_btn, write_help_and_back

menu_router = Router()


@menu_router.callback_query(F.data == 'guarantees')
async def guarantees_handler(callback: CallbackQuery):
    text = '''Игра в нашем боте работает с помощью стандартного стикера Telegram:

🎲

При отправке стикер показывает случайный результат. Причем рандом происходит на стороне Telegram, мы на него никак не влияем. Этот метод подробно описан в официальной документации (тут ссылка https://core.telegram.org/bots/api#senddice) для ботов. Соответственно, честность этих игр гарантируется самим Telegram.'''
    await edit_message(callback, text, reply_markup=await back_btn('start'))


@menu_router.callback_query(F.data == 'help')
async def guarantees_handler(callback: CallbackQuery):
    text = '''По любым вопросам обращайтесь к нашему оператору поддержки'''
    await edit_message(callback, text, reply_markup=await write_help_and_back())
