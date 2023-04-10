"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import json
from aiogram import Bot, Dispatcher, executor, types
from binance.client import Client

from config import TOKEN, SECRET_KEY, API_KEY


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
client = Client(API_KEY, SECRET_KEY)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")



@dp.message_handler()
async def echo(message: types.Message):
    btc_price_json = client.get_symbol_ticker(symbol="BTCUSDT")
    await message.answer(f"Bitcoin costs {btc_price_json['price']} USDT")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)