import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена из переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Путь к директории для сохранения изображений
IMAGE_DIR = './media/main'
VERT_DIR = os.path.join(IMAGE_DIR, 'vert')
HORIZ_DIR = os.path.join(IMAGE_DIR, 'horiz')

# Максимальное разрешение коллажа
MAX_WIDTH = 5000
MAX_HEIGHT = 4000
