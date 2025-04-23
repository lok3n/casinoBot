from aiogram import Router
from handlers.admin.admin_maling import mailing_router

admin_router = Router()
admin_router.include_routers(mailing_router)
