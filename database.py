import sqlite3
import time
import threading
from datetime import datetime
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
                "user_id"	INTEGER,
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


def add_record(task_data):
    '''
    Добавляет запись о задаче в базу данных.
    
    task_data: dictionary
        {
            'user_id': <user_id>,
            'id': <task_id>,
            'title': <task_title>,
            'description': <task_description>,
            'group': <task_group>,
            'time': <task_time>,
            'in_15': <bool>,
            'in_30': <bool>,
            'in_hour': <bool>,
            'in_day': <bool>,
            'in_week': <bool>
        }
    '''
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()
        
        # Подготовка SQL-запроса для вставки новой записи
        cursor.execute('''
            INSERT INTO tasks (
                user_id, id, title, description, "group", time, 
                in_15, in_30, in_hour, in_day, in_week
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data['user_id'], task_data['id'], task_data['title'], 
            task_data['description'], task_data['group'], task_data['time'], 
            task_data['in_15'], task_data['in_30'], task_data['in_hour'], 
            task_data['in_day'], task_data['in_week']
        ))

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
        ctext('success', 'Задача успешно добавлена в базу данных.')

    except sqlite3.Error as e:
        ctext('error', f'Ошибка при добавлении записи в базу данных: {e}')

def get_tasks_by_user_id(user_id):
    tasks = []
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()

        # Выполняем запрос для получения всех задач по user_id
        cursor.execute('''
            SELECT * FROM tasks WHERE user_id = ?
        ''', (user_id,))

        tasks = cursor.fetchall()

        conn.close()

    except sqlite3.Error as e:
        ctext('error', f'Ошибка при получении задач из базы данных: {e}')

    return tasks


def get_tasks_by_group_and_user(user_id, group):
    tasks = []
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()

        # Выполняем запрос для получения задач по user_id и group, сортировка по group
        cursor.execute('''
            SELECT * FROM tasks WHERE user_id = ? AND "group" = ? ORDER BY "group"
        ''', (user_id, group))

        tasks = cursor.fetchall()

        conn.close()

    except sqlite3.Error as e:
        ctext('error', f'Ошибка при получении задач из базы данных: {e}')

    return tasks


def get_task_by_id(task_id):
    task = None
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()

        # Выполняем запрос для получения задачи по её id
        cursor.execute('''
            SELECT * FROM tasks WHERE id = ?
        ''', (task_id,))

        task = cursor.fetchone()

        conn.close()

    except sqlite3.Error as e:
        ctext('error', f'Ошибка при получении задачи из базы данных: {e}')

    return task

def check_notifications():
    notifications = []
    try:
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()

        current_time = datetime.now()

        for task in tasks:
            task_time_str = task[5]  # Время задачи (6-й элемент)
            task_time = datetime.strptime(task_time_str, '%Y-%m-%d %H:%M')

            # Проверяем, настало ли время для уведомлений (сравниваем с текущим временем)
            if task_time <= current_time:
                user_id = task[0]  # user_id (первый элемент)
                in_15 = task[6]  # В 15 минут
                in_30 = task[7]  # В 30 минут
                in_hour = task[8]  # В час
                in_day = task[9]  # В день
                in_week = task[10]  # В неделю

                # Формируем уведомление
                if in_15:
                    notifications.append((user_id, f"15 минут перед: {task[2]} - {task[3]}"))
                if in_30:
                    notifications.append((user_id, f"30 минут перед: {task[2]} - {task[3]}"))
                if in_hour:
                    notifications.append((user_id, f"1 час перед: {task[2]} - {task[3]}"))
                if in_day:
                    notifications.append((user_id, f"1 день перед: {task[2]} - {task[3]}"))
                if in_week:
                    notifications.append((user_id, f"1 неделя перед: {task[2]} - {task[3]}"))

        conn.close()

    except sqlite3.Error as e:
        print(f'Ошибка при получении задач из базы данных: {e}')

    return notifications
    
if __name__ == "__main__":
    init_db()
    print(get_task_by_id('1011269'))
    print('---')
    print(get_tasks_by_group_and_user('11222', 'Work'))
    print('---')
    print(get_tasks_by_user_id('11222'))
