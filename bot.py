import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# Зображення патернів (тимчасові посилання)
patterns = [
    {
        "title": "Патерн: Голова і плечі",
        "image_url": "https://www.investopedia.com/thmb/MaNjJ9XJQ7O1WkwHL1kSA8MccLQ=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/headandshoulders1-5bfc69e4c9e77c00514e755b.png",
        "description": "Цей патерн сигналізує про можливий розворот тренду зверху вниз."
    },
    {
        "title": "Патерн: Подвійне дно",
        "image_url": "https://www.investopedia.com/thmb/qYBvRTFLzKKzv1B2Xvd-VByrbRY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/doublebottom-5bfc69f846e0fb002602b0c0.png",
        "description": "Цей патерн вказує на розворот тренду з низхідного на висхідний."
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Почати навчання", callback_data="start_learning")],
        [InlineKeyboardButton("Пройти тест", callback_data="start_quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вітаю! Оберіть дію:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_learning":
        for p in patterns:
            await query.message.reply_photo(photo=p["image_url"], caption=f"{p['title']}\n\n{p['description']}")
        await query.message.reply_text("Це всі базові патерни. Хочеш перевірити свої знання?", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Так, тест", callback_data="start_quiz")]
        ]))
    elif query.data == "start_quiz":
        keyboard = [
            [InlineKeyboardButton("Розворот тренду", callback_data="quiz_correct")],
            [InlineKeyboardButton("Продовження тренду", callback_data="quiz_wrong")]
        ]
        await query.message.reply_photo(
            photo=patterns[0]["image_url"],
            caption="Що означає цей патерн?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "quiz_correct":
        await query.message.reply_text("Правильно!")
    elif query.data == "quiz_wrong":
        await query.message.reply_text("Неправильно. Це сигнал розвороту тренду.")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_buttons))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def index():
    return "Бот працює."

async def set_webhook():
    await bot_app.bot.set_webhook(f"{WEBHOOK_URL}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    bot_app.run_polling()
