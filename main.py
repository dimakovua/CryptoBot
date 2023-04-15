"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import asyncio
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
is_monitoring = False

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

button_temp1 = KeyboardButton("Crypto price")
button_temp2 = KeyboardButton("Spot balance")
button_temp3 = KeyboardButton("Price monitoring")
button_temp4 = KeyboardButton("Stop monitoring")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_kb.add(button_temp1)
main_kb.add(button_temp2)
main_kb.add(button_temp3)
main_kb.add(button_temp4)

time_button1 = KeyboardButton("5 sec")
time_button2 = KeyboardButton("1 min")
time_button3 = KeyboardButton("30 min")
time_button4 = KeyboardButton("1 hour")
time_button5 = KeyboardButton("1 day")
time_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
time_kb.add(time_button1)
time_kb.add(time_button2)
time_kb.add(time_button3)
time_kb.add(time_button4)
time_kb.add(time_button5)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await bot.delete_webhook()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm CryptoBot!\nPowered by aiogram.", reply_markup=main_kb)


print(11111111)
@dp.message_handler(lambda message: message.text.strip() == 'Crypto price')
async def start_crypto_price(message: types.Message):
    global states
    states = "crypto_price"
    await message.answer("Please input cryptocurrency you want to check")
    print(55555555)


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

#################################
monitoring_task = None

async def get_btc_usdt_price(symbol: str):
    ticker = client.get_symbol_ticker(symbol=symbol + 'USDT')
    return float(ticker['price'])

async def send_crypto_usdt_price(message: types.Message, symbol: str):
    price = await get_btc_usdt_price(symbol)
    if price:
        await message.answer(f"Latest {symbol}/USDT price: ${price:.2f}", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Sorry, we couldn't fetch the price. Please try again later.")

async def price_update_loop(message: types.Message, interval: int, symbol: str):
    while True:
        await send_crypto_usdt_price(message, symbol)
        await asyncio.sleep(interval)  # set interval

@dp.message_handler(lambda message: message.text == 'Price monitoring')
async def start_price_monitoring(message: types.Message):
    global monitoring_task
    if monitoring_task is None:
        await message.reply("Enter the crypto symbol (e.g., ETH, BTC, APT, BUSD, etc.):")
    else:
        await message.reply("Price monitoring is already running. Stop it first.")

@dp.message_handler(regexp='^[A-Z]{2,5}$')
async def set_crypto_symbol(message: types.Message):
    global monitoring_task
    if monitoring_task is None:
        symbol = message.text
        await message.reply(f"Choose the monitoring interval for {symbol}/USDT:", reply_markup=time_kb)
    else:
        await message.reply("Price monitoring is already running. Stop it first.")

@dp.message_handler(lambda message: message.text in ['5 sec', '1 min', '30 min', '1 hour', '1 day'])
async def set_monitoring_interval(message: types.Message):
    global monitoring_task
    if monitoring_task is None:
        intervals = {
            '5 sec': 5,
            '1 min': 60,
            '30 min': 1800,
            '1 hour': 3600,
            '1 day': 86400
        }
        interval = intervals[message.text]
        await message.reply(f"Starting price monitoring every {message.text}...", reply_markup=main_kb)
        monitoring_task = asyncio.create_task(price_update_loop(message, interval))
    else:
        await message.reply("Price monitoring is already running. Stop it first.", reply_markup=main_kb)


@dp.message_handler(lambda message: message.text == 'Stop monitoring')
async def stop_price_monitoring(message: types.Message):
    global monitoring_task
    if monitoring_task is not None:
        monitoring_task.cancel()
        monitoring_task = None
        await message.reply("Stopping price monitoring...")
    else:
        await message.reply("Price monitoring is not running.")


@dp.message_handler()
async def process_crypto(message: types.Message, state: FSMContext):
    global states
    if (states == "crypto_price"):
        try:
            crypto_symbol = message.text.upper()
            btc_price_json = client.get_symbol_ticker(symbol=f"{crypto_symbol}USDT")
            states = ""
            await message.answer(f"{crypto_symbol} costs {round(float(btc_price_json['price']), 4)} USDT", reply_markup=main_kb)
        except:
            states = ""
            if (crypto_symbol=="USDT"):
                await message.answer(f"USDT costs 1.0000 USDT", reply_markup=main_kb)
            else:
                await message.answer(f"Please try again, no crypto available", reply_markup=main_kb)
    else:
        states = ""
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