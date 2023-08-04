from os import getenv
from dotenv import load_dotenv

load_dotenv()

# TELEGRAM
TELEGRAM_BOT_TOKEN: str | None = getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_SUPERUSER_ID: int | None = getenv('TELEGRAM_BOT_SUPERUSER_ID')

# DATABASE
DB_SERVER_PREFIX: str | None = getenv('DB_SERVER_PREFIX')
DB_SERVER_HOST: str | None = getenv('DB_SERVER_HOST')
DB_SERVER_PORT: int | None = getenv('DB_SERVER_PORT')
DB_AUTH_LOGIN: str | None = getenv('DB_AUTH_LOGIN')
DB_AUTH_PASSWORD: str | None = getenv('DB_AUTH_PASSWORD')
DB_NAME: str | None = getenv('DB_NAME')

DB_CONNECTION_STRING = (
    f'{DB_SERVER_PREFIX}://'
    f'{DB_AUTH_LOGIN}'
    f':{DB_AUTH_PASSWORD}@'
    f'{DB_SERVER_HOST}'
    f':{DB_SERVER_PORT}/'
    f'{DB_NAME}'
)
