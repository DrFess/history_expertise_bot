import asyncio
import logging

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from bot import schedule_handler
from bot.handlers import start_menu_handler
from bot.middleware import AllowedUserMiddleware
from settings import TOKEN, PROXY_URL


session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'), session=session)


async def scheduler():
    aioschedule.every().day.at('23:45').do(schedule_handler.start_scheduler)  # 07:45

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    dp = Dispatcher()
    dp.message.middleware(AllowedUserMiddleware())
    dp.include_routers(
        start_menu_handler.router,
    )

    asyncio.create_task(scheduler())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())