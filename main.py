import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import add_record  # Предполагается, что у вас есть функция для добавления данных в БД

bot = telebot.TeleBot(config.api_token)

# Словарь для хранения информации о текущем процессе
current_reminders = {}

# Функция для создания клавиатуры с категориями
def category_keyboard():
    keyboard = InlineKeyboardMarkup()
    categories = ["Личное 🏠", "Работа/Учеба 📚", "Здоровье 💊", "Важные даты 🎉", "Финансы 💰"]
    for category in categories:
        keyboard.add(InlineKeyboardButton(category, callback_data=f"category:{category}"))
    return keyboard

# Функция для создания клавиатуры с временем напоминания
def time_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    time_options = ["15 минут", "30 минут", "Час", "День", "Неделя"]

    # Если для пользователя уже выбраны временные напоминания, добавляем галочки
    selected_times = current_reminders.get(user_id, {}).get('time', [])

    for time in time_options:
        if time in selected_times:
            button_text = f"✅ {time}"
        else:
            button_text = f"❌ {time}"

        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"time:{time}:{user_id}"))

    keyboard.add(InlineKeyboardButton("Отправить", callback_data='send'))
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Для создания уведомления нажми кнопку 'Создать уведомление'.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Создать уведомление", callback_data="create_notification")
        )
    )

# Обработчик нажатия на кнопку "Создать уведомление"
@bot.callback_query_handler(func=lambda call: call.data == "create_notification")
def create_notification(call):
    user_id = call.message.chat.id
    current_reminders[user_id] = {'user_id': user_id}  # Инициализация данных

    bot.send_message(user_id, "Введите название уведомления:")
    bot.register_next_step_handler(call.message, get_title)

# Получение названия уведомления
def get_title(message):
    user_id = message.chat.id
    current_reminders[user_id]['title'] = message.text

    bot.send_message(user_id, "Введите описание уведомления:")
    bot.register_next_step_handler(message, get_description)

# Получение описания уведомления
def get_description(message):
    user_id = message.chat.id
    current_reminders[user_id]['description'] = message.text

    bot.send_message(user_id, "Выберите категорию для уведомления:", reply_markup=category_keyboard())

# Обработка выбора категории
@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def get_category(call):
    user_id = call.message.chat.id
    category = call.data.split(":")[1]
    current_reminders[user_id]['group'] = category

    bot.send_message(user_id, "Выберите, за какое время нужно напомнить:", reply_markup=time_keyboard(user_id))

# Обработка выбора времени для напоминания
@bot.callback_query_handler(func=lambda call: call.data.startswith('time:'))
def get_time_reminder(call):
    user_id = call.message.chat.id
    time_info = call.data.split(":")
    reminder_time = time_info[1]

    if 'time' not in current_reminders[user_id]:
        current_reminders[user_id]['time'] = []

    if reminder_time in current_reminders[user_id]['time']:
        current_reminders[user_id]['time'].remove(reminder_time)
    else:
        current_reminders[user_id]['time'].append(reminder_time)

    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text="Выберите дополнительные сроки для напоминания, если необходимо, или нажмите 'Отправить'.",
        reply_markup=time_keyboard(user_id)
    )

# Обработка кнопки "Отправить"
@bot.callback_query_handler(func=lambda call: call.data == 'send')
def send_notification(call):
    user_id = call.message.chat.id
    reminder_data = current_reminders.get(user_id, {})

    if all(key in reminder_data for key in ['user_id', 'title', 'description', 'group', 'time']):
        reminder_data_to_db = {
            'user_id': reminder_data['user_id'],
            'id': hash((reminder_data['user_id'], reminder_data['title'])),  # Генерация уникального ID
            'title': reminder_data['title'],
            'description': reminder_data['description'],
            'group': reminder_data['group'],
            'time': ", ".join(reminder_data['time']),
            'in_15': "15 минут" in reminder_data['time'],
            'in_30': "30 минут" in reminder_data['time'],
            'in_hour': "Час" in reminder_data['time'],
            'in_day': "День" in reminder_data['time'],
            'in_week': "Неделя" in reminder_data['time'],
        }
        add_record(reminder_data_to_db)
        bot.send_message(user_id, "Уведомление успешно создано и добавлено в базу данных.")
    else:
        bot.send_message(user_id, "Ошибка. Все данные должны быть заполнены.")

    if user_id in current_reminders:
        del current_reminders[user_id]

# Запуск бота
if __name__ == "__main__":
    bot.polling()
