from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


async def back_btn(callback) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='↩️ Назад', callback_data=callback).as_markup()


async def write_help_and_back() -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder()
            .button(text='👤 Написать', url=f'https://t.me/dicejet_manager')
            .button(text='↩️ Назад', callback_data='start').adjust(1).as_markup())


async def again_with_back(callback: str, bet: int, back_callback: str) -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder()
            .button(text=f'🔄 Играть еще – ставка {bet}₽', callback_data=f"{callback} {bet}")
            .button(text='↩️ Изменить ставку', callback_data=back_callback)
            .button(text='🏠︎ Главное меню', callback_data='start').adjust(1).as_markup())


async def play_with_back(callback: str, back_callback: str, balance: int, free_balance: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if free_balance:
        builder.button(text='🚀 Играть бесплатно', callback_data=f'{callback} 0')
    bets = [50, 100, 200, 500, 1000]
    for bet in bets:
        if balance >= bet:
            builder.button(text=f'{bet} RUB', callback_data=f'{callback} {bet}')
    builder.button(text='↩️ Назад', callback_data=back_callback)
    return builder.adjust(1).as_markup()


async def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🎲 Играть', callback_data='dice')
    builder.button(text='💰 Баланс', callback_data='wallet')
    builder.button(text='💯 Гарантии', callback_data='guarantees')
    builder.button(text='❓ Помощь', callback_data='help')
    if is_admin:
        builder.button(text='📨 Рассылка', callback_data='admin_mailing')
        # builder.button(text='👑 Админ-панель', callback_data='admin_panel')
    return builder.adjust(2).as_markup()


async def wallet_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='📥 Пополнить', callback_data='wallet_topup')
    # builder.button(text='📤 Вывести', callback_data='wallet_withdraw')
    builder.button(text='📤 Вывести', callback_data='help')
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(2).as_markup()


async def amount_wallet_kb(callback) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    amount = [500, 1000, 2500, 5000]
    for sum in amount:
        builder.button(text=f'{sum} RUB', callback_data=f'{callback} {sum}')
    builder.button(text='↩️ Назад', callback_data='wallet')
    return builder.adjust(3).as_markup()


async def choice_type_withdraw() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='💎 USDT', callback_data='choice_type_wallet USDT')
    builder.button(text='🟣 ЮМани', callback_data='choice_type_wallet YOOMONEY')
    builder.button(text='🍀 Clever', callback_data='choice_type_wallet CLEVER')
    builder.button(text='🏛️ По СБП', callback_data='choice_type_wallet SBP')
    builder.button(text='💳 На карту', callback_data='choice_type_wallet CARD')
    builder.button(text='📲 На телефон', callback_data='choice_type_wallet PHONE')
    builder.button(text='↩️ Назад', callback_data='wallet')
    return builder.adjust(1).as_markup()


async def pay_btn(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='💳 Оплатить', url=url).as_markup()


async def submit_kb(submit, cancel):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтвердить', callback_data=submit)
    builder.button(text='❌ Отменить', callback_data=cancel)
    return builder.adjust(2).as_markup()
