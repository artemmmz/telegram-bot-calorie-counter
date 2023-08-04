import logging

from aiogram import Bot, Dispatcher, executor

from config import TELEGRAM_BOT_TOKEN
from handlers import register_all_handlers


async def __on_startup():
    register_all_handlers()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(bot)
    executor.start_polling(dispatcher=dp, on_startup=__on_startup)
