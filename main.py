from sys import stdout
from asyncio import run
from os import getenv
from logging import basicConfig, INFO
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from handlers import *
from utils.models import Users, Payments, Withdraws

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_routers(start_router, user_router, admin_router)


async def main():
    tables = [Users, Payments, Withdraws]
    for table in tables:
        if not table.table_exists():
            table.create_table()

    print('started')
    # basicConfig(level=INFO, stream=stdout)
    basicConfig(filename='logs.log', level=INFO)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню')])

    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
