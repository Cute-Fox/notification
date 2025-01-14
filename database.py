import sqlite3
from color_text import *
import config
import os

def init_db():
    db_path = config.db_path
    if not os.path.exists(db_path):
        ctext('error', f'Ошибка: база данных "{db_path}" не найдена!')
        return  # Выход из функции, если база данных не существует
    
    try:
        # Подключаемся к существующей базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        ctext('info', f'Успешное подключение к базе данных "{db_path}"')

        # Создаем таблицу для задач (если её еще нет)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                "user_id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "id"	INTEGER UNIQUE,
                "title"	TEXT,
                "description"	INTEGER,
                "group"	TEXT,
                "time"	TEXT,
                "in_15"	BLOB,
                "in_30"	INTEGER,
                "in_hour"	INTEGER,
                "in_day"	INTEGER,
                "in_week"	INTEGER
            )
        ''')

        conn.commit()
        conn.close()
        ctext('success', 'Таблица успешно создана или уже существует.')

    except sqlite3.Error as e:
        ctext('error', f'Ошибка подключения или работы с базой данных: {e}')

if __name__ == "__main__":
    init_db()