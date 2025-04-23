from aiogram.fsm.state import State, StatesGroup


class Wallet(StatesGroup):
    topup_choice = State()
    withdraw_choice = State()
    withdraw_wallet = State()


class Play(StatesGroup):
    bet_dice = State()


class Admin(StatesGroup):
    input_text_mailing = State()
