import logging
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Database setup
conn = sqlite3.connect("crypto_game.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

# Logging setup
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start_game():
    if request.method == 'POST':
        user_id = request.form['user_id']
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.execute("INSERT INTO users (id, balance) VALUES (?, ?)", (user_id, 1000))
            conn.commit()
            return redirect(url_for('game', user_id=user_id))
        else:
            return redirect(url_for('game', user_id=user_id))
    return render_template('start.html')

@app.route('/game/<user_id>', methods=['GET', 'POST'])
def game(user_id):
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()

    if not balance:
        return redirect(url_for('start_game'))

    if request.method == 'POST':
        trade_amount = random.randint(-500, 500)
        new_balance = balance[0] + trade_amount
        cursor.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, user_id))
        conn.commit()
        trade_result = f"You made a profit of {trade_amount} coins!" if trade_amount > 0 else f"You lost {-trade_amount} coins!"
        return render_template('game.html', user_id=user_id, balance=new_balance, trade_result=trade_result)

    return render_template('game.html', user_id=user_id, balance=balance[0])

@app.route('/balance/<user_id>')
def check_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()
    if balance:
        return f"Your current balance: {balance[0]} coins"
    else:
        return "You're not registered yet. Use /start to join the game."

if __name__ == '__main__':
    app.run(debug=True)
