import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from utils.keyboards import back_btn, submit_kb
from aiogram.fsm.context import FSMContext
from utils.states import Admin
from filters.admin import IsAdmin
from utils.models import Users
from aiogram.exceptions import TelegramForbiddenError

mailing_router = Router()


@mailing_router.callback_query(IsAdmin(), F.data == 'admin_mailing')
async def admin_mailing_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('ℹ️ Введите текст, который хотите отправить по всей базе пользователей',
                                     reply_markup=await back_btn('start'))
    await state.set_state(Admin.input_text_mailing)
    await state.update_data(past_msg_id=callback.message.message_id)


@mailing_router.message(IsAdmin(), Admin.input_text_mailing)
async def input_text_mailing(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    await state.clear()
    await message.bot.edit_message_text(message.text,
                                        parse_mode="HTML",
                                        chat_id=message.from_user.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=await submit_kb('submit_admin_mail', 'start'))


@mailing_router.callback_query(IsAdmin(), F.data == 'submit_admin_mail')
async def submit_admin_mail_handle(callback: CallbackQuery):
    users = Users.select()
    sending_text = callback.message.text
    await callback.message.edit_text('⏳ В процессе . . .')
    for user in users:
        try:
            await callback.bot.send_message(user.user_id, sending_text, parse_mode="HTML")
        except TelegramForbiddenError as e:
            pass
            # logging.info(f'error while admin mailing msg to user - {e}\nDELETED FROM DATABASE - {user.user_id}')
            # user.delete_instance()
    await callback.message.edit_text('✅ Успешно!', reply_markup=await back_btn('start'))
