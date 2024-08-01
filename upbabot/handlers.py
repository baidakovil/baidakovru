import os
from telegram import Update
from telegram.ext import CallbackContext
from config import IMAGE_DIR, VERT_DIR, HORIZ_DIR, MAX_WIDTH, MAX_HEIGHT
from utils import update_image_list
from image_processing import create_collage
from PIL import Image


# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Отправь мне изображение, и я сохраню его на сервере.'
    )


# Обработчик изображений
async def handle_image(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = os.path.join(IMAGE_DIR, file.file_path.split('/')[-1])
    await file.download_to_drive(file_path)

    # Определяем ориентацию изображения
    with Image.open(file_path) as img:
        if img.height > img.width:
            dest_path = os.path.join(VERT_DIR, os.path.basename(file_path))
        else:
            dest_path = os.path.join(HORIZ_DIR, os.path.basename(file_path))
        os.rename(file_path, dest_path)

    vert_count, horiz_count = update_image_list()
    await update.message.reply_text(
        f'Изображение сохранено! Теперь на сервере {vert_count} вертикальных и {horiz_count} горизонтальных изображений.'
    )


# Обработчик команды /horiz
async def send_horiz_collage(update: Update, context: CallbackContext) -> None:
    horiz_images = [
        os.path.join(HORIZ_DIR, f)
        for f in os.listdir(HORIZ_DIR)
        if os.path.isfile(os.path.join(HORIZ_DIR, f))
    ]
    if not horiz_images:
        await update.message.reply_text(
            'Нет горизонтальных изображений для создания коллажа.'
        )
        return

    collage = create_collage(horiz_images, MAX_WIDTH, MAX_HEIGHT)
    collage_path = os.path.join(IMAGE_DIR, 'horiz_collage.jpg')
    collage.save(collage_path)

    await context.bot.send_document(
        chat_id=update.message.chat_id, document=open(collage_path, 'rb')
    )


# Обработчик команды /vert
async def send_vert_collage(update: Update, context: CallbackContext) -> None:
    vert_images = [
        os.path.join(VERT_DIR, f)
        for f in os.listdir(VERT_DIR)
        if os.path.isfile(os.path.join(VERT_DIR, f))
    ]
    if not vert_images:
        await update.message.reply_text(
            'Нет вертикальных изображений для создания коллажа.'
        )
        return

    collage = create_collage(vert_images, MAX_WIDTH, MAX_HEIGHT)
    collage_path = os.path.join(IMAGE_DIR, 'vert_collage.jpg')
    collage.save(collage_path)

    await context.bot.send_document(
        chat_id=update.message.chat_id, document=open(collage_path, 'rb')
    )
