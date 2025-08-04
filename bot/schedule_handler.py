from aiogram import Router
from aiogram.filters import Command
from requests import Session

from bot.main import bot
from settings import admin, proxies
from utils.check_history_functions import check_history

router = Router()


@router.message(Command(commands=['scheduler']))
async def start_scheduler():
    session = Session()  # создание сессии подключения
    session.proxies.update(proxies)
    result = check_history(session)
    session.close()
    await bot.send_message(chat_id=admin, text=result)
