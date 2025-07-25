# bot.py

import logging
import requests
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Импортируем настройки
from config import TELEGRAM_BOT_TOKEN, API_KEY, API_URL, MODEL_NAME

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Задай мне любой вопрос, и я постараюсь ответить.")

# Отправка запроса в Qwen3 через API
def get_qwen_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            # Убираем теги <think> и лишние пробелы
            clean_answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
            return clean_answer
        else:
            return f"Ошибка API: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Произошла ошибка: {e}"

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = get_qwen_response(user_message)
    await update.message.reply_text(reply)

# Основная функция запуска
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Токен бота не установлен в config.py")

    print("Бот запускается...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Только один раз!

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()