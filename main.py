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

from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types

# Import the FSM and its states
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup


states = ""

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

sum_btc = 0.0
balances = client.get_account()
for _balance in balances["balances"]:
        asset = _balance["asset"]
        if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
            try:
                btc_quantity = float(_balance["free"]) + float(_balance["locked"])
                if asset == "BTC":
                    sum_btc += btc_quantity
                else:
                    _price = client.get_symbol_ticker(symbol=asset + "BTC")
                    sum_btc += btc_quantity * float(_price["price"])
                    print(asset+" ")
                    print(btc_quantity)
            except:
                pass

current_btc_price_USD = client.get_symbol_ticker(symbol="BTCUSDT")["price"]
own_usd = sum_btc * float(current_btc_price_USD)
usdt_balance = client.get_asset_balance(asset='USDT')
own_usd += float(usdt_balance['free'])
sum_btc += float(usdt_balance['free'])/float(current_btc_price_USD)
print(" * Spot => %.8f BTC == " % sum_btc, end="")
print("%.8f USDT" % own_usd)

button_temp1 = KeyboardButton("Crypto price")
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

#@dp.message_handler(lambda message: message.text == '🤑BTC/USDT')
#async def echo(message: types.Message):
#    btc_price_json = client.get_symbol_ticker(symbol="BTCUSDT")
#    await message.answer(f"Bitcoin costs {btc_price_json['price']} USDT", reply_markup=main_kb)
print(11111111)
@dp.message_handler(lambda message: message.text.strip() == 'Crypto price')
async def start_crypto_price(message: types.Message):
    global states
    states = "crypto_price"
    await message.answer("Please input cryptocurrency you want to check")
    print(55555555)

print(222222222)
if (states == "crypto_price"):
    @dp.message_handler()
    async def process_crypto(message: types.Message, state: FSMContext):
        crypto_symbol = message.text.upper()
        print(66666666)
        btc_price_json = client.get_symbol_ticker(symbol=f"{crypto_symbol}USDT")
        await message.answer(f"{crypto_symbol} costs {btc_price_json['price']} USDT", reply_markup=main_kb)



print(33333333)
@dp.message_handler(lambda message: message.text == 'Spot balance')
async def echo(message: types.Message):
    sum_btc = 0.0
    crypto_prices = {}
    balances = client.get_account()
    for _balance in balances["balances"]:
        asset = _balance["asset"]
        if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
            try:
                btc_quantity = float(_balance["free"]) + float(_balance["locked"])
                if asset == "BTC":
                    sum_btc += btc_quantity
                else:
                    _price = client.get_symbol_ticker(symbol=asset + "BTC")
                    sum_btc += btc_quantity * float(_price["price"])
                    crypto_prices[asset] = btc_quantity
            except:
                pass

    current_btc_price_USD = client.get_symbol_ticker(symbol="BTCUSDT")["price"]
    own_usd = sum_btc * float(current_btc_price_USD)
    usdt_balance = client.get_asset_balance(asset='USDT')
    own_usd += float(usdt_balance['free'])
    sum_btc += float(usdt_balance['free'])/float(current_btc_price_USD)
    sum_btc = round(sum_btc, 6)
    own_usd = round(own_usd, 4)
    result_string = ""
    for symbol, price in crypto_prices.items():
        result_string += f"{price} {symbol}\n"
    result_string += f"{usdt_balance['free']} USDT\n"
    result_string += f"Balance equivalent in BTC - {sum_btc} BTC\n"
    result_string += f"Balance equivalent in USDT - {own_usd} USDT"
    await message.answer(result_string, reply_markup=main_kb)

print(44444444)
@dp.message_handler()
async def echo(message: types.Message):
    print(77777777)
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