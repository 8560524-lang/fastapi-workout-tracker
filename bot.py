import telebot
import requests

TOKEN = "8684550432:AAEiXUim-H-1D8vwr7pxKh6qunBzt-IWqTI"
bot = telebot.TeleBot(TOKEN)
API_URL = "http://127.0.0.1:8000"

user_tokens = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "🏋️ **Фітнес-Бот для FastAPI**\n\n"
        "Доступні команди:\n"
        "1. `/register` — автоматична реєстрація\n"
        "2. `/login` — авторизація та отримання токена\n"
        "3. `/add <назва>` — додати вправу (напр: `/add Жим 3x10`)\n"
        "4. `/list` — переглянути свої вправи\n"
        "5. `/delete <id>` — видалити вправу за її номером\n"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['register'])
def register_user(message):
    telegram_id = message.chat.id
    email = f"user_{telegram_id}@telegram.com"
    password = "secure_password_123"

    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": email, "password": password}
        )
        if response.status_code == 201:
            bot.reply_to(message, f"✅ Тебе зареєстровано як `{email}`! Тепер виконай `/login`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ Інформація від сервера: {response.text}")
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "❌ Не вдалося з'єднатися з API.")

@bot.message_handler(commands=['login'])
def login_user(message):
    telegram_id = message.chat.id
    email = f"user_{telegram_id}@telegram.com"
    password = "secure_password_123"

    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            user_tokens[telegram_id] = token
            bot.reply_to(message, "🔑 **Успішний вхід!** JWT-токен збережено. Тепер ти можеш керувати тренуваннями.",
                         parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Помилка входу: {response.text}")
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "❌ Помилка підключення до сервера.")

@bot.message_handler(commands=['add'])
def add_workout(message):
    telegram_id = message.chat.id
    token = user_tokens.get(telegram_id)

    if not token:
        bot.reply_to(message, "🔒 Спочатку виконай команду `/login`, щоб отримати доступ!")
        return

    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        bot.reply_to(message, "⚠️ Напиши вправу після команди. Приклад: `/add Присідання 4x12`", parse_mode="Markdown")
        return

    workout_data = text_parts[1]
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            f"{API_URL}/workouts/",
            json={
                "title": workout_data,
                "type": "Силове",
                "duration_minutes": 45
            },
            headers=headers
        )
        if response.status_code in [200, 201]:
            bot.reply_to(message, f"💪 Вправу **«{workout_data}»** успішно збережено в базі!", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ Помилка збереження: {response.text}")
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "❌ Немає зв'язку з сервером.")

@bot.message_handler(commands=['list'])
def get_workouts(message):
    telegram_id = message.chat.id
    token = user_tokens.get(telegram_id)

    if not token:
        bot.reply_to(message, "🔒 Спочатку виконай команду `/login`!")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{API_URL}/workouts/",
            headers=headers
        )
        if response.status_code == 200:
            workouts = response.json()
            if not workouts:
                bot.reply_to(message, "📋 Твій список тренувань поки порожній. Додай щось через `/add`!")
                return

            msg_text = "🏋️ **Твої збережені тренування:**\n\n"
            for w in workouts:
                w_id = w.get("id")
                title = w.get("title", "Без назви")
                msg_text += f"🆔 **{w_id}**: {title}\n"

            bot.reply_to(message, msg_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ Помилка отримання даних: {response.text}")
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "❌ Помилка підключення до сервера.")

@bot.message_handler(commands=['delete'])
def delete_workout(message):
    telegram_id = message.chat.id
    token = user_tokens.get(telegram_id)

    if not token:
        bot.reply_to(message, "🔒 Спочатку виконай команду `/login`!")
        return

    text_parts = message.text.split()
    if len(text_parts) < 2 or not text_parts[1].isdigit():
        bot.reply_to(message, "⚠️ Вкажи коректний ID тренування. Приклад: `/delete 3`", parse_mode="Markdown")
        return

    workout_id = text_parts[1]
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{API_URL}/workouts/{workout_id}",
            headers=headers
        )

        if response.status_code in [200, 204]:
            bot.reply_to(message, f"🗑️ Тренування 🆔 {workout_id} успішно видалено!")
        elif response.status_code == 404:
            bot.reply_to(message, f"❌ Тренування з ID {workout_id} не знайдено.")
        else:
            bot.reply_to(message, f"⚠️ Не вдалося видалити: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "❌ Помилка підключення до сервера.")

print("Бот запущений і чекає на команди...")
bot.polling(none_stop=True)