"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import json
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, message
from binance.client import Client

from config import TOKEN, SECRET_KEY, API_KEY


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
client = Client(API_KEY, SECRET_KEY)

button_temp = KeyboardButton("🤑BTC/USDT")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_kb.add(button_temp)

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
    executor.start_polling(dp, skip_updates=True)