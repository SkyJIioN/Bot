import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # наприклад: https://your-bot.onrender.com

# Приклади уроків зі справжніми зображеннями
lessons = [
    {
        "title": "Патерн: Голова і плечі",
        "image": "https://www.tradingwithrayner.com/wp-content/uploads/2019/10/head-and-shoulders-pattern.jpg"
    },
    {
        "title": "Патерн: Подвійне дно",
        "image": "https://www.tradingwithrayner.com/wp-content/uploads/2019/10/double-bottom-pattern.jpg"
    }
]

# Тестове питання
test_question = {
    "question": "Що означає патерн 'Голова і плечі'?",
    "options": ["Сигнал до росту", "Сигнал до падіння", "Флет"],
    "correct": 1
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Почати навчання", callback_data="start_lessons")],
        [InlineKeyboardButton("Пройти тест", callback_data="start_test")]
    ]
    await update.message.reply_text(
        "Вітаю! Обери дію:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обробник кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_lessons":
        context.user_data["lesson_index"] = 0
        await send_lesson(update, context)

    elif query.data == "next_lesson":
        context.user_data["lesson_index"] += 1
        await send_lesson(update, context)

    elif query.data == "start_test":
        await send_test_question(update, context)

    elif query.data.startswith("answer_"):
        selected = int(query.data.split("_")[1])
        if selected == test_question["correct"]:
            await query.edit_message_text("Правильно!")
        else:
            await query.edit_message_text("Неправильно. Спробуй ще раз!")

# Відправка уроку
async def send_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("lesson_index", 0)
    if index < len(lessons):
        lesson = lessons[index]
        keyboard = []
        if index + 1 < len(lessons):
            keyboard = [[InlineKeyboardButton("Далі", callback_data="next_lesson")]]

        try:
            await update.callback_query.message.reply_photo(
                photo=lesson["image"],
                caption=lesson["title"],
                reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
            )
        except Exception as e:
            await update.callback_query.message.reply_text(
                f"{lesson['title']} (зображення не вдалося завантажити)",
                reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
            )
    else:
        await update.callback_query.message.reply_text("Це була остання тема!")

# Відправка тестового питання
async def send_test_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(option, callback_data=f"answer_{i}")]
        for i, option in enumerate(test_question["options"])
    ]
    await update.callback_query.message.reply_text(
        test_question["question"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Запуск бота через webhook
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )
