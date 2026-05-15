from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.freemodel.dev/v1"
)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {"role": "user", "content": text}
        ]
    )

    reply = response.choices[0].message.content

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(
    os.getenv("BOT_TOKEN")
).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
)

print("Bot running...")
app.run_polling()
