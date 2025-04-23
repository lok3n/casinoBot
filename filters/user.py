import os
from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.models import Users


class NotBanned(BaseFilter):  # [1]
    async def __call__(self, message: Message) -> bool:  # [3]
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if not user:
            return True
        return False if user.banned else True
