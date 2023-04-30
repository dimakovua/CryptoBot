"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import asyncio
import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from binance.client import Client

from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types

from config import TOKEN, API_KEY, SECRET_KEY
from keyboards import Keyboards

kb = Keyboards()
states = ""
is_monitoring = False

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
client = Client(API_KEY, SECRET_KEY)

#-----------------------------------------------------------------------------#

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm CryptoBot!\nPowered by aiogram.", reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text.strip() == 'Crypto price')
async def start_crypto_price(message: types.Message):
    global states
    states = "crypto_price"
    await message.answer("Please input cryptocurrency you want to check")
    print(55555555)

#-----------------------------------------------------------------------------#

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
    await message.answer(result_string, reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#
################################# ALERT
monitoring_task = None
monitoring_flag = False
ticker = ""
current_state = None
alert_task = None

@dp.message_handler(lambda message: message.text == 'Crypto alert')
async def start_crypto_alert(message: types.Message):
    global current_state
    current_state = 'alert_symbol'
    await message.reply("Enter the crypto symbol (e.g., ETH, BTC, APT, BUSD, etc.):")

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: current_state == 'alert_symbol', regexp='^[A-Z]{2,10}$')
async def set_crypto_alert_symbol(message: types.Message):
    global current_state
    current_state = {'symbol': message.text, 'state': 'alert_change'}
    symbol = current_state['symbol']
    try:
        aboba = await get_btc_usdt_price(symbol)
        await message.reply("Choose the % of price change to trigger the alert:", reply_markup=kb.alert_change_kb)
    except:
        current_state = 'alert_symbol'
        await message.answer(f"Please try to insert crypto ticker again.")

#-----------------------------------------------------------------------------#

async def crypto_alert_loop(message: types.Message, symbol: str, change: float):
    global alert_task
    initial_price = await get_btc_usdt_price(symbol)
    target_price_upper = initial_price * (1 + change / 100)
    target_price_lower = initial_price * (1 - change / 100)
    while True:
        current_price = await get_btc_usdt_price(symbol)
        if current_price >= target_price_upper or current_price <= target_price_lower:
            alert_task = None
            await message.reply(f"{symbol}/USDT price changed by {change}%. Initial price: ${initial_price:.3f}, Current price: ${current_price:.3f}", reply_markup=kb.main_kb)
            break
        await asyncio.sleep(5)  # You can adjust the frequency of price checking here
        if alert_task is None:
            break

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: current_state is not None and current_state.get('state') == 'alert_change', Text(equals=['0.01', '0.1', '1', '5', '10']))
async def set_crypto_alert_change(message: types.Message):
    global current_state, alert_task
    symbol = current_state['symbol']
    change = float(message.text)
    current_state = None
    current_price = await get_btc_usdt_price(symbol)
    await message.reply(f"Starting crypto alert for {symbol}/USDT with {change}% change. Current price: ${current_price:.3f}", reply_markup=kb.main_kb)
    alert_task = asyncio.create_task(crypto_alert_loop(message, symbol, change))

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text == 'Stop crypto alert')
async def stop_crypto_alert(message: types.Message):
    global alert_task
    if alert_task is not None:
        alert_task.cancel()
        alert_task = None
        await message.reply("Crypto alert stopped.", reply_markup=kb.main_kb)
    else:
        await message.reply("No crypto alert is currently active.", reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#
##################################### MONITORING

async def get_btc_usdt_price(symbol: str):
    ticker = client.get_symbol_ticker(symbol=symbol + 'USDT')
    return float(ticker['price'])

#-----------------------------------------------------------------------------#

async def send_crypto_usdt_price(message: types.Message, symbol: str):
    price = await get_btc_usdt_price(symbol)
    if price:
        await message.answer(f"Latest {symbol}/USDT price: ${price:.2f}", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Sorry, we couldn't fetch the price. Please try again later.")

async def price_update_loop(message: types.Message, interval: int, symbol: str):
    global monitoring_flag
    monitoring_flag = True
    while monitoring_flag:
        await send_crypto_usdt_price(message, symbol)
        await asyncio.sleep(interval)  # set interval

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text == 'Price monitoring')
async def start_price_monitoring(message: types.Message):
    global monitoring_task
    global states
    if monitoring_task is None:
        states = "monitoring"
        await message.reply("Enter the crypto symbol (e.g., ETH, BTC, APT, BUSD, etc.):")
    else:
        await message.reply("Price monitoring is already running. Stop it first.")

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: states == "monitoring", regexp='^[A-Z]{2,10}$')
async def set_crypto_symbol(message: types.Message):
    global ticker 
    ticker = message.text #####
    try:
        aboba = await get_btc_usdt_price(ticker)
        global monitoring_task
        if monitoring_task is None:
            symbol = message.text
            await message.reply(f"Choose the monitoring interval for {symbol}/USDT:", reply_markup=kb.time_kb)
        else:
            await message.reply("Price monitoring is already running. Stop it first.")
    except:
        await message.answer(f"Please try to insert crypto ticker again.")

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text in ['5 sec', '1 min', '30 min', '1 hour', '1 day'])
async def set_monitoring_interval(message: types.Message):
    global monitoring_task
    global monitoring_flag
    global ticker
    if monitoring_task is None and not monitoring_flag:
        intervals = {
            '5 sec': 5,
            '1 min': 60,
            '30 min': 1800,
            '1 hour': 3600,
            '1 day': 86400
        }
        interval = intervals[message.text]
        await message.reply(f"Starting price monitoring for {ticker}/USDT every {message.text}...", reply_markup=kb.main_kb)
        monitoring_task = asyncio.create_task(price_update_loop(message, interval, ticker))
    else:
        await message.reply("Price monitoring is already running. Stop it first.", reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text == 'Stop monitoring')
async def stop_price_monitoring(message: types.Message):
    global monitoring_task
    global monitoring_flag
    if monitoring_task is not None:
        monitoring_flag = False
        monitoring_task.cancel()
        monitoring_task = None
        await message.reply("Stopping price monitoring...", reply_markup=kb.main_kb)
    else:
        await message.reply("Price monitoring is not running.", reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#

@dp.message_handler(lambda message: states == "crypto_price")                   ### Optimised
async def process_crypto(message: types.Message, state: FSMContext):
    global states
    states = ""
    try:
        crypto_symbol = message.text.upper()
        btc_price_json = client.get_symbol_ticker(symbol=f"{crypto_symbol}USDT")
        await message.answer(f"{crypto_symbol} costs {round(float(btc_price_json['price']), 4)} USDT", reply_markup=kb.main_kb)
    except:
        if (crypto_symbol=="USDT"):
            await message.answer(f"USDT costs 1.0000 USDT", reply_markup=kb.main_kb)
        else:
            await message.answer(f"Please try again, no crypto available", reply_markup=kb.main_kb)

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
