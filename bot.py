import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8157933236:AAEzi5QzHTlh3FAvln82zAxeUH_d_D9PAmo"

# Дані поетапного навчання
patterns = [
    {
        "title": "Патерн «Голова і плечі»",
        "description": "Цей патерн сигналізує про можливий розворот тренду зверху вниз.",
        "image_url": "https://i.imgur.com/G6mnDFf.png"  # Відкрите зображення
    },
    {
        "title": "Патерн «Подвійна вершина»",
        "description": "Формується після зростання, сигналізує про зміну на спад.",
        "image_url": "https://i.imgur.com/7WOUtTk.png"
    }
]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_step(update, context, 0)

# Надсилання навчального етапу
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
    
    if update_or_callback.callback_query:
        await update_or_callback.callback_query.edit_message_media(
            media=InputMediaPhoto(media=pattern["image_url"], caption=f"*{pattern['title']}*\n\n{pattern['description']}", parse_mode="Markdown"),
            reply_markup=reply_markup
        )
    else:
        await update_or_callback.message.reply_photo(
            photo=pattern["image_url"],
            caption=f"*{pattern['title']}*\n\n{pattern['description']}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# Обробка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("step_"):
        step = data.split("_")[1]
        await send_step(update, context, step)
    elif data == "quiz":
        await query.edit_message_caption(
            caption="🧪 *Міні-тест буде додано пізніше.*",
            parse_mode="Markdown"
        )

# Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
