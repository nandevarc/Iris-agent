from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters
from openai import OpenAI
import os

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

bot = Bot(token=TOKEN)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.freemodel.dev/v1"
)

app = Flask(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)

async def chat(update, context):
    try:
        text = update.message.text

        response = client.chat.completions.create(
            model="gpt-5.5",
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

dispatcher.add_handler(
    MessageHandler(filters.TEXT, chat)
)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
