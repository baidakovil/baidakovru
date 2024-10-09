# update_data.py

from services import github
import sqlite3


def update_all_services():
    # Подключаемся к базе данных
    conn = sqlite3.connect('./db/services.db')
    cursor = conn.cursor()

    # Обновляем GitHub
    github_update = github.get_last_update('baidakovil')
    cursor.execute(
        "UPDATE services SET last_update=? WHERE name=?", (github_update, 'GitHub')
    )

    # Аналогично для других сервисов
    # ...

    conn.commit()
    conn.close()
