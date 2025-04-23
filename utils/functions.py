import os

from aiogram.types import CallbackQuery, Message
from aiogram import Bot


async def edit_message(event: CallbackQuery | Message, text: str, photo: str = None, **kwargs):
    """Functional for editing/answer messages, it looks like changing one message"""
    if isinstance(event, Message):
        if event.from_user.is_bot:
            return await event.edit_text(text, **kwargs)
        else:
            return await event.answer(text, **kwargs)

    msg = None
    if event.message.text is None:
        await event.message.delete()
        if photo and photo != 'none':
            msg = await event.message.answer_photo(photo, caption=text, **kwargs)
        else:
            msg = await event.message.answer(text, **kwargs)
    elif photo and photo != 'none':
        await event.message.delete()
        msg = await event.message.answer_photo(photo, caption=text, **kwargs)
    else:
        await event.message.edit_text(text, **kwargs)

    return msg if msg else event.message


async def notify_admins(bot: Bot, text: str, **kwargs):
    for admin in os.getenv('ADMINS').split(','):
        try:
            await bot.send_message(int(admin), text, **kwargs)
        except:
            pass


async def is_admin(user_id: int):
    return user_id in map(int, os.getenv('ADMINS').split(','))


async def send_emoji_win(event: CallbackQuery | Message, value: int):
    emoji = ''
    if value == 1:
        emoji = '🚀'
    elif value == 2:
        emoji = '🎉'
    elif value == 3:
        emoji = '🥳'
    elif value == 4:
        emoji = '💣'
    elif value == 5:
        emoji = '🔥'
    elif value == 6:
        emoji = '⚡️'
    await event.answer(emoji) if isinstance(event, Message) else await event.message.answer(emoji)
