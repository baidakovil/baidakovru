import os
import json
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from PIL import Image
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()
# Получение токена из переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Путь к директории для сохранения изображений
IMAGE_DIR = './media/main'
VERT_DIR = os.path.join(IMAGE_DIR, 'vert')
HORIZ_DIR = os.path.join(IMAGE_DIR, 'horiz')

# Создаем директории, если они не существуют
os.makedirs(VERT_DIR, exist_ok=True)
os.makedirs(HORIZ_DIR, exist_ok=True)

# Максимальное разрешение коллажа
MAX_WIDTH = 5000
MAX_HEIGHT = 4000


# Функция для обновления JSON файла с именами изображений
def update_image_list():
    vert_images = [
        f for f in os.listdir(VERT_DIR) if os.path.isfile(os.path.join(VERT_DIR, f))
    ]
    horiz_images = [
        f for f in os.listdir(HORIZ_DIR) if os.path.isfile(os.path.join(HORIZ_DIR, f))
    ]
    image_list = {'vert': vert_images, 'horiz': horiz_images}
    with open(os.path.join(IMAGE_DIR, 'images.json'), 'w') as f:
        json.dump(image_list, f)
    return len(vert_images), len(horiz_images)


# Функция для создания коллажа
def create_collage(image_paths, max_width, max_height):
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(img.size for img in images))

    total_width = sum(widths)
    max_height = max(heights)

    if total_width > max_width:
        scale_factor = max_width / total_width
        total_width = max_width
        max_height = int(max_height * scale_factor)
        images = [
            img.resize((int(img.width * scale_factor), int(img.height * scale_factor)))
            for img in images
        ]

    if max_height > max_height:
        scale_factor = max_height / max_height
        max_height = max_height
        total_width = int(total_width * scale_factor)
        images = [
            img.resize((int(img.width * scale_factor), int(img.height * scale_factor)))
            for img in images
        ]

    collage = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for img in images:
        collage.paste(img, (x_offset, 0))
        x_offset += img.width

    return collage


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


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CommandHandler('horiz', send_horiz_collage))
    application.add_handler(CommandHandler('vert', send_vert_collage))

    application.run_polling()


if __name__ == '__main__':
    main()
