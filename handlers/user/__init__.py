from aiogram import Router
from handlers.user.menu import menu_router
from handlers.user.dice import dice_router
from handlers.user.wallet import wallet_router

user_router = Router()
user_router.include_routers(menu_router, dice_router, wallet_router)
