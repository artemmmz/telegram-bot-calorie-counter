from aiogram import Dispatcher, types


async def command_start(message: types.Message) -> None:
    await message.answer("Start")


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(command_start, commands=['start'])
