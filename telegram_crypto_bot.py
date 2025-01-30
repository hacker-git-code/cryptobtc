import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import sqlite3
import random

API_TOKEN = "7862150347:AAGrXZfQ-uGaVeQriABQ2OxuvApz9VBhio4s"

# Logging setup
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Database setup
conn = sqlite3.connect("crypto_game.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

@dp.message_handler(commands=['start'])
async def start_game(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute("INSERT INTO users (id, balance) VALUES (?, ?)", (user_id, 1000))
        conn.commit()
        await message.reply("Welcome to the Crypto Game! You have been given 1000 coins to start trading.")
    else:
        await message.reply("You're already registered! Use /balance to check your coins.")

@dp.message_handler(commands=['balance'])
async def check_balance(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()
    
    if balance:
        await message.reply(f"Your current balance: {balance[0]} coins")
    else:
        await message.reply("You're not registered yet. Use /start to join the game.")

@dp.message_handler(commands=['trade'])
async def trade_crypto(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()
    
    if not balance:
        await message.reply("You're not registered yet. Use /start to join the game.")
        return
    
    trade_amount = random.randint(-500, 500)
    new_balance = balance[0] + trade_amount
    cursor.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, user_id))
    conn.commit()
    
    if trade_amount > 0:
        await message.reply(f"You made a profit of {trade_amount} coins! New balance: {new_balance}")
    else:
        await message.reply(f"You lost {-trade_amount} coins! New balance: {new_balance}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
