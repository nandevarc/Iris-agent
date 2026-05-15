from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI
import asyncio
import os

# ENV
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# OPENAI CLIENT
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

# FLASK
app = Flask(__name__)

# TELEGRAM APP
telegram_app = Application.builder().token(TOKEN).build()

# EVENT LOOP GLOBAL
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif.")

# CHAT FUNCTION
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah Hypatia, AI assistant Telegram. "
                        "Gunakan bahasa Indonesia santai, natural, "
                        "jelas, singkat, dan membantu."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.7,
            max_tokens=500,
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# HANDLERS
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
)

# INIT TELEGRAM
loop.run_until_complete(telegram_app.initialize())

# WEBHOOK
@app.post(f"/{TOKEN}")
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )

    loop.run_until_complete(
        telegram_app.process_update(update)
    )

    return "ok"

# ROOT
@app.get("/")
def home():
    return "Bot running"

# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
