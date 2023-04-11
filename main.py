"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, message
from binance.client import Client

#from config import TOKEN, SECRET_KEY, API_KEY

TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
# Webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
client = Client(API_KEY, SECRET_KEY)
print(client.get_asset_balance(asset='BTC'))

button_temp1 = KeyboardButton("🤑BTC/USDT")
button_temp2 = KeyboardButton("Spot balance")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_kb.add(button_temp1)
main_kb.add(button_temp2)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await bot.delete_webhook()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm CryptoBot!\nPowered by aiogram.", reply_markup=main_kb)

@dp.message_handler(lambda message: message.text == '🤑BTC/USDT')
async def echo(message: types.Message):
    btc_price_json = client.get_symbol_ticker(symbol="BTCUSDT")
    await message.answer(f"Bitcoin costs {btc_price_json['price']} USDT", reply_markup=main_kb)

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Use button")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )