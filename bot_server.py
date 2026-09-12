import os
import telebot
from flask import Flask, request
from telebot import types
import threading 
TOKEN = os.environ.get("BOT_TOKEN", "8775188168:AAE2cabcMzxWqSRsxS-M6AFLeFRPxxBITxI")
CHAT_ID = "252915499"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

is_active = False
active_pair = "ALL"
active_tf = "ALL"

PAIRS = ["AUD/JPY", "CHF/JPY", "EUR/GBP", "EUR/CHF", "EUR/USD", "USD/CAD", "GBP/USD", "AUD/CAD", "USD/CHF", "AUD/USD", "EUR/AUD", "XAU/USD", "BTC/USD"]
TIMEFRAMES = ["M1", "M3", "M5", "M15", "1H", "4H"]

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    toggle_btn = types.KeyboardButton("🔴 ВЫКЛЮЧИТЬ АНАЛИЗ") if is_active else types.KeyboardButton("🟢 ВКЛЮЧИТЬ АНАЛИЗ")
    markup.add(toggle_btn)
    markup.add(types.KeyboardButton("🌐 ВСЕ ПАРЫ"), types.KeyboardButton("⏱ ВСЕ ТАЙМФРЕЙМЫ"))
    markup.add(*[types.KeyboardButton(p) for p in PAIRS])
    markup.add(*[types.KeyboardButton(tf) for tf in TIMEFRAMES])
    return markup

@bot.message_handler(commands=["start"])
def start_message(message):
    status_text = "🟢 ВКЛЮЧЁН" if is_active else "🔴 ВЫКЛЮЧЁН"
    bot.send_message(message.chat.id, f"⚙️ Панель управления\n\nСтатус: {status_text}\nПара: {active_pair}\nТФ: {active_tf}", parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(content_types=["text"])
def handle_text(message):
    global is_active, active_pair, active_tf
    text = message.text.upper()
    if "ВКЛЮЧИТЬ АНАЛИЗ" in text:
        is_active = True
        bot.send_message(message.chat.id, f"🟢 Запущено! Пара: {active_pair} | ТФ: {active_tf}", parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif "ВЫКЛЮЧИТЬ АНАЛИЗ" in text:
        is_active = False
        bot.send_message(message.chat.id, "🔴 Остановлено.", parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif text == "🌐 ВСЕ ПАРЫ":
        active_pair = "ALL"
        bot.send_message(message.chat.id, "🌐 Выбраны ВСЕ ПАРЫ.")
    elif text == "⏱ ВСЕ ТАЙМФРЕЙМЫ":
        active_tf = "ALL"
        bot.send_message(message.chat.id, "⏱ Выбраны ВСЕ ТАЙМФРЕЙМЫ.")
    elif text in [p.upper() for p in PAIRS]:
        active_pair = text.replace("/", "")
        bot.send_message(message.chat.id, f"🎯 Пара: {text}", parse_mode="Markdown")
    elif text in TIMEFRAMES:
        active_tf = text
        bot.send_message(message.chat.id, f"⏱ ТФ: {text}", parse_mode="Markdown")

@app.route("/mt5-multi-data", methods=["POST"])
def webhook():
    global is_active, active_pair, active_tf
    if not is_active:
        return "Disabled", 200
    data = request.get_data(as_text=True)
    if "SUPERTREND" in data.upper():
        bot.send_message(CHAT_ID, f"🚨 Сигнал [SuperTrend] по {active_pair}!\n\n{data}")
    elif "RSI" in data.upper():
        bot.send_message(CHAT_ID, f"🚨 Сигнал [RSI] по {active_pair}!\n\n{data}")
    elif "MACD" in data.upper():
        bot.send_message(CHAT_ID, f"🚨 Сигнал [MACD] по {active_pair}!\n\n{data}")
    elif "ICHIMOKU" in data.upper():
        bot.send_message(CHAT_ID, f"🚨 Сигнал [Ichimoku] по {active_pair}!\n\n{data}")

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    print("Бот и Flask запущены...")
    app.run(host="0.0.0.0", port=10000)
