import sqlite3

# Подключаемся к базе данных (если её нет, она будет создана)
conn = sqlite3.connect('services.db')
cursor = conn.cursor()

# Создаем таблицу services
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    last_update TEXT
)
'''
)

# Вставляем начальные данные
services = [
    ('GitHub', None),
    # Добавьте здесь другие сервисы, если они есть
]

cursor.executemany('INSERT INTO services (name, last_update) VALUES (?, ?)', services)

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("База данных создана успешно.")
