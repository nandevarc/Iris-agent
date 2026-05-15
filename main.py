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

client = OpenAI(api_key=OPENAI_API_KEY)

# FLASK
app = Flask(__name__)

# TELEGRAM
telegram_app = Application.builder().token(TOKEN).build()

# COMMAND START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif.")

# CHAT AI
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant.",
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# HANDLER
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
)

# WEBHOOK
@app.post(f"/{TOKEN}")
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)

    async def process():
        await telegram_app.initialize()
        await telegram_app.process_update(update)

    asyncio.run(process())

    return "ok"

# ROOT
@app.get("/")
def home():
    return "Bot running"

# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
