from PIL import Image


# Функция для создания коллажа
def create_collage(image_paths, max_width, max_height):
    images = [Image.open(path) for path in image_paths]
    num_images = len(images)

    # Определяем количество изображений по горизонтали и вертикали
    num_columns = int(num_images**0.5)
    num_rows = (num_images + num_columns - 1) // num_columns  # Округление вверх

    # Рассчитываем размеры каждого изображения в коллаже
    thumb_width = max_width // num_columns
    thumb_height = max_height // num_rows

    # Создаем пустой коллаж
    collage = Image.new('RGB', (max_width, max_height))

    # Располагаем изображения в сетке
    for index, img in enumerate(images):
        img.thumbnail((thumb_width, thumb_height))
        x = (index % num_columns) * thumb_width
        y = (index // num_columns) * thumb_height
        collage.paste(img, (x, y))

    return collage
