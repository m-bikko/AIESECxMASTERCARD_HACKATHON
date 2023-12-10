import telebot
from telebot import types
import schedule
import time
import openai
from openai import OpenAI
import re

API_KEY = 'your-token'
TOKEN = "your-token"
openai.api_key = API_KEY
bot = telebot.TeleBot(TOKEN)

client = OpenAI(
    api_key=API_KEY,
)

last_films_message = None  # Добавим переменную для хранения последнего сообщения с фильмами
list_of_user_ids = []
films = [
    {"id": 1, "title": "Доктор Стрэндж", "description": "Страшная автокатастрофа поставила крест на карьере "
                                                        "успешного нейрохирурга Доктора Стрэнджа. Отчаявшись, "
                                                        "он отправляется в путешествие в поисках исцеления и "
                                                        "открывает в себе невероятные способности к "
                                                        "трансформации пространства и времени. Теперь он — "
                                                        "связующее звено между параллельными измерениями, "
                                                        "а его миссия — защищать жителей Земли и "
                                                        "противодействовать злу, какое бы обличие оно ни "
                                                        "принимало", "year": 2016,
     "rating": 7.5,
     "image_url": "https://klike.net/uploads/posts/2023-01/1674376326_3-64.jpg"},
    {"id": 2, "title": "Человек-паук: Возвращение домой", "description": "После встречи с командой Мстителей Питер "
                                                                         "Паркер возвращается домой и пытается жить "
                                                                         "обычной жизнью под опекой тёти Мэй. Но "
                                                                         "теперь за Питером приглядывает кое-кто ещё. "
                                                                         "Тони Старк видел Человека-паука в деле и "
                                                                         "должен стать его наставником. Когда новый "
                                                                         "злодей Стервятник угрожает уничтожить всё, "
                                                                         "что дорого Питеру, приходит время показать "
                                                                         "всем, что такое настоящий супергерой.",
     "year": 2017, "rating": 7.2,
     "image_url": "https://w.forfun.com/fetch/f7/f75edc64cb09b305313b2303d7af4abe.jpeg"},
]

theaters = [
    {"id": 1, "name": "Chaplin", "film_id": 1, "price": 2500},
    {"id": 2, "name": "Cinemax 2", "film_id": 1, "price": 1100},
    {"id": 3, "name": "Kinopark 3", "film_id": 2, "price": 900},
    {"id": 4, "name": "Kinoforum 4", "film_id": 2, "price": 1800},
]

last_films_message = None


def send_new_movie_notification_to_all_users():
    global bot
    global list_of_user_ids
    print(list_of_user_ids)

    for user_id in list_of_user_ids:
        bot.send_photo(chat_id=user_id, photo=films[0]['image_url'],
                       caption=f"<b>ПРЕМЬЕРА</b>\n{films[0]['title']}\n\n{films[0]['description']}\n\nРейтинг: {films[0]['rating']}/10",
                       reply_markup=create_inline_keyboard(films[0]['id']),
                       parse_mode="HTML")


def send_new_movie_notification_to_all_users2():
    global bot
    global list_of_user_ids
    print(list_of_user_ids)

    for user_id in list_of_user_ids:
        bot.send_message(chat_id=user_id, text="Чтобы спросить у ИИ что-то, начните вводить \"порекомендуй\"...")


# send_new_movie_notification_to_all_users2()

# Запустить задачу каждые 10 минут
schedule.every(10).minutes.do(send_new_movie_notification_to_all_users2)
# send_new_movie_notification_to_all_users2()

# Создать инлайн-клавиатуру для кнопки "Купить"
def create_inline_keyboard(film_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"Купить", callback_data=f"buy_{film_id}"))
    return keyboard


# Запустить задачу каждые 1 минут
schedule.every(600).seconds.do(send_new_movie_notification_to_all_users)


# Функция для запуска планировщика
def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


user_profiles = {}


@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    print("help by id", user_id)

    # Список команд
    commands_list = [
        "/start - Начать использование бота",
        "/balance - Проверить текущий баланс",
        "/purchases - Посмотреть количество покупок билетов",
        "/meetings - Посмотреть количество встреч с друзьями",
        "/profile - Посмотреть информацию о профиле",
        "/help - Вывести список доступных команд"
    ]

    # Отправить список команд
    bot.send_message(user_id, "\n".join(commands_list))


# Обработчик команды /profile
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.from_user.id
    print("profile by id", user_id)

    # Получить или создать профиль пользователя
    profile = user_profiles.get(user_id, {"purchases": 0, "balance": 0, "rating": 0, "meetings": 0})

    # Отправить информацию о профиле
    bot.send_message(user_id, f"Ваш профиль:\n"
                              f"Количество покупок билетов: {profile['purchases']}\n"
                              f"Текущий баланс: {profile['balance']}\n"
                              f"Рейтинг: {profile['rating']}\n"
                              f"Количество встреч с друзьями: {profile['meetings']}")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    print("start by id", user_id)
    user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    phone_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    user_markup.add(phone_button)
    bot.send_message(message.from_user.id, "Добро пожаловать! Пожалуйста, отправьте свой номер телефона.",
                     reply_markup=user_markup)


# Обработчик контакта
@bot.message_handler(content_types=['contact'])
def handle_contact(message):

    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    list_of_user_ids.append(user_id)
    user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    print(f"Пользователь с ID {user_id} зарегистрирован с номером телефона: {phone_number}")
    watch_films = types.KeyboardButton(text="Посмотреть фильмы")
    buy_films = types.KeyboardButton(text="Купить билет на фильм")
    profile = types.KeyboardButton(text="/profile")
    user_markup.add(watch_films)
    user_markup.add(buy_films)
    user_markup.add(profile)
    # Отправить сообщение без маркапа
    bot.send_message(user_id, "Спасибо за предоставленный номер телефона.", reply_markup=user_markup)


@bot.message_handler(func=lambda message: message.text == 'Купить билет на фильм')
def handle_by_films(message):
    global last_films_message
    user_id = message.from_user.id
    print("Купить билет на фильм by id", user_id)
    films_markup = types.InlineKeyboardMarkup()
    for film in films:
        films_markup.add(
            types.InlineKeyboardButton(text=f"{film['title']} - Купить", callback_data=f"buy_{film['id']}"))

    last_films_message = bot.send_message(message.from_user.id, "Список фильмов:", reply_markup=films_markup)


@bot.message_handler(regexp=r'^порекомендуй (.+)$')
def handle_recommendation(message):
    user_id = message.from_user.id
    print("user by id", user_id, message)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Представь себя ассистентом в кинотеатре и ты должен давать мне информация о ближайших "
                           "сеансов. И веди себя как реальный человек, отвечай вежливо и не веди себя как бот."
                           "Ты знаешь фильмы начиная только с 2020 года и все свободные залы в кинотеатрах. Просто"
                           "дай :  " + message.text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion)
    bot.send_message(message.chat.id, f"{chat_completion.choices[0].message.content}")


@bot.message_handler(func=lambda message: message.text == 'Посмотреть фильмы')
def handle_show_all_films(message):
    global last_films_message
    user_id = message.from_user.id
    print("Посмотреть фильмы by id", user_id)
    for film in films:
        bot.send_photo(message.from_user.id, film['image_url'],
                       caption=f"{film['title']} ({film['year']})\nОценка: {film['rating']}\n{film['description']}")

    films_markup = types.InlineKeyboardMarkup()
    for film in films:
        films_markup.add(
            types.InlineKeyboardButton(text=f"{film['title']} - Купить", callback_data=f"buy_{film['id']}"))

    last_films_message = bot.send_message(message.from_user.id, "Список всех фильмов:", reply_markup=films_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy_film(call):
    film_id = int(call.data.split('_')[1])
    film = next((f for f in films if f['id'] == film_id), None)
    if film:
        theaters_for_film = [theater for theater in theaters if theater['film_id'] == film_id]
        if theaters_for_film:
            theaters_markup = types.InlineKeyboardMarkup()
            for theater in theaters_for_film:
                theaters_markup.add(types.InlineKeyboardButton(text=f"{theater['name']} - Цена: {theater['price']}",
                                                               callback_data=f"confirm_{theater['id']}"))
            theaters_markup.row(types.InlineKeyboardButton(text="Назад", callback_data="back"))
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text=f"Выберите кинотеатр для фильма {film['title']}:", reply_markup=theaters_markup)
        else:
            bot.send_message(call.from_user.id, f"Для фильма {film['title']} кинотеатры не найдены.")
    else:
        bot.send_message(call.from_user.id, f"Фильм с ID {film_id} не найден.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def handle_confirm_purchase(call):
    theater_id = int(call.data.split('_')[1])
    theater = next((t for t in theaters if t['id'] == theater_id), None)
    if theater:
        bot.send_message(call.from_user.id,
                         f"Вы выбрали кинотеатр {theater['name']} с ценой {theater['price']}. Теперь вы можете продолжить с покупкой билетов.")
    else:
        bot.send_message(call.from_user.id, f"Кинотеатр с ID {theater_id} не найден.")


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def handle_back_button(call):
    global last_films_message
    films_markup = types.InlineKeyboardMarkup()
    for film in films:
        films_markup.add(
            types.InlineKeyboardButton(text=f"{film['title']} - Купить", callback_data=f"buy_{film['id']}"))

    bot.edit_message_text(chat_id=call.from_user.id, message_id=last_films_message.message_id, text="Список фильмов:",
                          reply_markup=films_markup)


if __name__ == '__main__':
    import threading

    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    bot.polling(none_stop=True)
