import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode
from telegram.ext.webhookhandler import WebhookServer

from flask import Flask, request

# Токен і URL
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8157933236:AAEzi5QzHTlh3FAvln82zAxeUH_d_D9PAmo"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Вставиш тут свій URL з Render

app = Flask(__name__)

# Дані
patterns = [
    {
        "title": "Патерн «Голова і плечі»",
        "description": "Сигнал розвороту зростаючого тренду вниз.",
        "image_url": "https://i.imgur.com/G6mnDFf.png"
    },
    {
        "title": "Патерн «Подвійна вершина»",
        "description": "Формація, що передбачає спад тренду.",
        "image_url": "https://i.imgur.com/7WOUtTk.png"
    }
]

quiz_questions = [
    {
        "question": "Який патерн сигналізує про зміну висхідного тренду?",
        "options": ["Голова і плечі", "Флет", "Трикутник"],
        "correct_index": 0
    }
]
user_quiz_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_step(update, context, 0)

async def send_step(update_or_callback, context, step):
    step = int(step)
    pattern = patterns[step]
    keyboard = []

    if step > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"step_{step - 1}")])
    if step < len(patterns) - 1:
        keyboard.append([InlineKeyboardButton("➡️ Далі", callback_data=f"step_{step + 1}")])
    else:
        keyboard.append([InlineKeyboardButton("🧪 До тесту", callback_data="quiz")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_callback, "callback_query"):
        await update_or_callback.callback_query.edit_message_media(
            media=InputMediaPhoto(
                media=pattern["image_url"],
                caption=f"*{pattern['title']}*\n\n{pattern['description']}",
                parse_mode=ParseMode.MARKDOWN
            ),
            reply_markup=reply_markup
        )
    else:
        await update_or_callback.message.reply_photo(
            photo=pattern["image_url"],
            caption=f"*{pattern['title']}*\n\n{pattern['description']}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("step_"):
        step = data.split("_")[1]
        await send_step(update, context, step)
    elif data == "quiz":
        await start_quiz(update, context)
    elif data.startswith("quiz_answer_"):
        await handle_quiz_answer(update, context)

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    user_quiz_state[user_id] = 0

    try:
        await update.callback_query.message.delete()
    except Exception:
        pass

    await send_quiz_question(update, context, user_id)

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    q_index = user_quiz_state[user_id]
    q = quiz_questions[q_index]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"quiz_answer_{i}")]
        for i, opt in enumerate(q["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=f"🧪 *Питання {q_index + 1}:*\n{q['question']}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    q_index = user_quiz_state.get(user_id, 0)
    q = quiz_questions[q_index]

    selected = int(update.callback_query.data.split("_")[-1])
    correct = q["correct_index"]

    if selected == correct:
        response = "✅ Правильно!"
    else:
        response = f"❌ Неправильно. Правильна відповідь: {q['options'][correct]}"

    await update.callback_query.edit_message_text(
        text=response + "\n\nНавчання завершено! Використай /start, щоб пройти ще раз.",
        parse_mode="Markdown"
    )
    user_quiz_state.pop(user_id, None)

@app.route("/", methods=["GET"])
def index():
    return "Бот працює!"

async def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))

    await app_bot.initialize()
    await app_bot.bot.set_webhook(url=WEBHOOK_URL)
    await app_bot.start()
    await app_bot.updater.start_polling()
    return app_bot

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
