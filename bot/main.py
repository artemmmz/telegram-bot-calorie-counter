import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN, DEBUG
from handlers import register_all_handlers
from utils.texts import i18n


async def __on_startup(dp: Dispatcher):
    register_all_handlers(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
    bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.setup_middleware(i18n)

    executor.start_polling(
        dispatcher=dp, skip_updates=not DEBUG, on_startup=__on_startup
    )
