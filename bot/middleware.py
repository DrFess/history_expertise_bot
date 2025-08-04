import logging

from aiogram import Dispatcher, BaseMiddleware
from aiogram.types import Message

from settings import ALLOWED_USERS


async def allowed_user_middleware(dispatcher: Dispatcher, handler):
    async def middleware_handler(event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            if user_id not in ALLOWED_USERS:
                logging.info(f"Неразрешённый пользователь ({user_id}) пытался отправить сообщение. Игнорируем.")
                return
        return await handler(event, data)
    return middleware_handler


class AllowedUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            if user_id not in ALLOWED_USERS:
                logging.info(f"Неразрешённый пользователь ({user_id}) пытался отправить сообщение. Игнорируем.")
                return
        return await handler(event, data)