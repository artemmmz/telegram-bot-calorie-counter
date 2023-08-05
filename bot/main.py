import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers import register_all_handlers


async def __on_startup(dp: Dispatcher):
    register_all_handlers(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dispatcher=dp, on_startup=__on_startup)
