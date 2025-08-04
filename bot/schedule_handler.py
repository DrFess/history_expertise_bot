from aiogram import Router
from aiogram.filters import Command

from utils.L2.diaries import create_diaries_function

router = Router()


@router.message(Command(commands=['scheduler']))
async def start_scheduler():
    print('Запущен процесс создания дневников')
    if create_diaries_function():
        print('Дневники созданы, проверяй')
    else:
        print('Что-то пошло не так')
