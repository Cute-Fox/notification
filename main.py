import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ваш токен от BotFather
TOKEN = "7858668499:AAEMcrJsMqKwvpLzs86SN80bJIRgUSl7w5A"
bot = telebot.TeleBot(TOKEN)

# Категории уведомлений
categories = [
    "Личное 🏠",
    "Работа/Учеба 💼📚",
    "Здоровье 🏋️‍♀️💊",
    "Важные даты 📅🎉",
    "Финансы 💰📈"
]

# Хранилище напоминаний
reminders = {category: {} for category in categories}  # Словарь {категория: {user_id: [напоминания]}}

# Главное меню
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Список уведомлений", callback_data="list_reminders"))
    markup.add(InlineKeyboardButton("Создать уведомление", callback_data="create_reminder"))
    return markup

# Меню категорий
def category_menu(callback_prefix):
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(InlineKeyboardButton(category, callback_data=f"{callback_prefix}:{category}"))
    markup.add(InlineKeyboardButton("Назад в меню", callback_data="main_menu"))
    return markup

# Обработчик команды /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для создания напоминаний. Вы можете управлять своими напоминаниями с помощью кнопок ниже.",
        reply_markup=main_menu()
    )

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "list_reminders":
        bot.edit_message_text(
            "Выберите категорию для просмотра уведомлений:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=category_menu("view_category")
        )
    elif call.data.startswith("view_category:"):
        category = call.data.split(":")[1]
        user_id = call.from_user.id
        if category == "Все":
            all_reminders = "\n\n".join(
                f"Категория: {cat}\n" + "\n".join(f"{i+1}. {rem}" for i, rem in enumerate(reminders[cat].get(user_id, [])))
                for cat in categories if user_id in reminders[cat]
            ) or "У вас нет напоминаний."
            bot.edit_message_text(
                all_reminders,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=category_menu("view_category")
            )
        else:
            category_reminders = "\n".join(
                [f"{i+1}. {rem}" for i, rem in enumerate(reminders[category].get(user_id, []))]
            ) or "Нет напоминаний в этой категории."
            markup = InlineKeyboardMarkup()
            for i, reminder in enumerate(reminders[category].get(user_id, [])):
                markup.add(InlineKeyboardButton(f"Удалить {i+1}", callback_data=f"delete_reminder:{category}:{i}"))
            markup.add(InlineKeyboardButton("Назад в категории", callback_data="list_reminders"))
            markup.add(InlineKeyboardButton("Назад в меню", callback_data="main_menu"))
            bot.edit_message_text(
                f"Напоминания в категории '{category}':\n\n{category_reminders}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
    elif call.data.startswith("delete_reminder:"):
        category, index = call.data.split(":")[1], int(call.data.split(":")[2])
        user_id = call.from_user.id
        try:
            del reminders[category][user_id][index]
            bot.edit_message_text(
                f"Напоминание удалено из категории '{category}'.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=main_menu()
            )
        except IndexError:
            bot.send_message(
                call.message.chat.id,
                "Ошибка: Напоминание не найдено.",
                reply_markup=main_menu()
            )
    elif call.data == "create_reminder":
        bot.edit_message_text(
            "Выберите категорию для нового уведомления:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=category_menu("create_in_category")
        )
    elif call.data.startswith("create_in_category:"):
        category = call.data.split(":")[1]
        msg = bot.edit_message_text(
            f"Введите текст уведомления для категории '{category}':",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.register_next_step_handler(msg, save_reminder, category)
    elif call.data == "main_menu":
        bot.edit_message_text(
            "Вы вернулись в главное меню.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

# Сохранение напоминания
def save_reminder(message, category):
    user_id = message.from_user.id
    reminder_text = message.text

    if user_id not in reminders[category]:
        reminders[category][user_id] = []
    reminders[category][user_id].append(reminder_text)

    bot.send_message(
        message.chat.id,
        f"Напоминание '{reminder_text}' сохранено в категории '{category}'!",
        reply_markup=main_menu()
    )

# Запуск бота
bot.polling()