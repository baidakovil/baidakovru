import os
import json
from config import IMAGE_DIR, VERT_DIR, HORIZ_DIR


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
