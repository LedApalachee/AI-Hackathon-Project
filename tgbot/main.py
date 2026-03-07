import os
from ultralytics import YOLO
import measure_plant as mp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8693729462:AAGpBDskdqkCUtOvDbKsDYvCPVnW9uaU31I"

model = YOLO("measure_plant.pt")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Отправь мне картинку или сразу несколько - я всё обработаю и верну измерения."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]

    # скачиваем файл
    file = await context.bot.get_file(photo.file_id)
    filename = file.file_unique_id + ".jpg"
    await file.download_to_drive(f"unprocessed/{filename}")

    # прогоняем через модель
    objects = mp.measure(model, f"unprocessed/{filename}", 9, f"segmented/{filename}")

    # формируем подпись, сколько чего измерено
    leaves = []
    stems = []
    roots = []
    for obj in objects:
        if obj["classname"] == "leaf":
            leaves += [obj["amount"]]
        elif obj["classname"] == "stem":
            stems += [obj["amount"]]
        else:
            roots += [obj["amount"]]
        
    result_str = ""
    if len(leaves) > 0:
        result_str += "Лист: " if len(leaves) == 1 else "Листья: "
        result_str += "; ".join(str(leaf) for leaf in leaves) + " мм2\n"
    if len(stems) > 0:
        result_str += "Стебль: " if len(stems) == 1 else "Стебли: "
        result_str += "; ".join(str(stem) for stem in stems) + " мм\n"
    if len(roots) > 0:
        result_str += "Корень: " if len(roots) == 1 else "Корни: "
        result_str += "; ".join(str(root) for root in roots) + " мм\n"

    # отправляем обратно
    await update.message.reply_photo(photo = open(f"segmented/{filename}", "rb"), caption = result_str)
    
    # чистим временные файлы
    os.remove(f"unprocessed/{filename}")
    os.remove(f"segmented/{filename}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()


if __name__ == "__main__":
    main()
