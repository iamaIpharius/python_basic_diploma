import telebot
from decouple import config
from telebot.types import InputMediaPhoto

from botrequests import lowprice
import sqlite3

TOKEN = config('TOKEN')

bot = telebot.TeleBot(TOKEN)
conn = sqlite3.connect('history.db', check_same_thread=False)

c = conn.cursor()


def insert_row(value):
    user = 'user' + str(value.from_user.id)
    c.execute(f"INSERT INTO {user} VALUES ('{value.text}', '*', '*', '*', '*', '*')")
    conn.commit()


def update_db(value, column):
    user = 'user' + str(value.from_user.id)
    c.execute(f"""UPDATE {user} SET {column} = "{str(value.text)}" WHERE rowid = (SELECT MAX(rowid) FROM {user})""")
    conn.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = 'user' + str(message.from_user.id)
    c.execute(f"""CREATE TABLE IF NOT EXISTS {user} (
    command text,
    city text,
    hotels_count text,
    check_in text,
    check_out text,
    photos text
    )""")
    conn.commit()
    bot.reply_to(message, "( ͡° ͜ʖ ͡°)")


@bot.message_handler(commands=['helloworld'])
def send_welcome(message):
    bot.reply_to(message, "Hello, World!")


@bot.message_handler(commands=['lowprice'])
def lowprice_start(message):
    insert_row(message)

    bot.send_message(message.from_user.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(message, where_we_going)


def where_we_going(message):
    update_db(message, 'city')


    bot.send_message(message.from_user.id, 'Сколько отелей нужно вывести в поиске? ')
    bot.register_next_step_handler(message, how_many_hotels)


def how_many_hotels(message):
    update_db(message, 'hotels_count')
    user = 'user' + str(message.from_user.id)
    bot.send_message(message.from_user.id, 'Дата заезда в формате yyyy-MM-dd: ')
    bot.register_next_step_handler(message, set_check_in)


def set_check_in(message):
    update_db(message, 'check_in')
    bot.send_message(message.from_user.id, 'Дата выезда в формате yyyy-MM-dd: ')
    bot.register_next_step_handler(message, set_check_out)


def set_check_out(message):
    update_db(message, 'check_out')
    bot.send_message(message.from_user.id, 'Нужны ли фотографии? (да/нет) ')
    bot.register_next_step_handler(message, need_photos)


def need_photos(message):
    update_db(message, 'photos')
    bot.send_message(message.from_user.id, 'ОБРАБАТЫВАЮ...')

    user = 'user' + str(message.from_user.id)
    c.execute(f"SELECT * FROM {user}")
    table = c.fetchall()
    work_row = table[-1]
    print(work_row)

    if message.text.lower() == "да":
        bot.send_message(message.from_user.id, 'ИЩУ ФОТО...')
        dest_id = lowprice.get_destination_id(work_row[1])
        current_hotels_list = lowprice.hotels_list_by_lowprice(dest_id, work_row[2], work_row[3], work_row[4])
        for hotel in current_hotels_list:
            info_about_hotel = lowprice.form_result_string(hotel)
            current_photos_list = lowprice.get_photos(hotel['id'])
            current_photos_list = [x.format(size='b') for x in current_photos_list]
            media_array = [InputMediaPhoto(x) for x in current_photos_list[:9]]
            media_array[0].caption = info_about_hotel
            bot.send_media_group(message.from_user.id, media_array)

    else:
        bot.send_message(message.from_user.id, 'ПОДОЖДИТЕ...')
        dest_id = lowprice.get_destination_id(work_row[1])
        current_hotels_list = lowprice.hotels_list_by_lowprice(dest_id, work_row[2], work_row[3], work_row[4])
        for hotel in current_hotels_list:
            info_about_hotel = lowprice.form_result_string(hotel)
            bot.send_message(message.from_user.id, info_about_hotel)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if 'привет' in message.text.lower():

        bot.send_message(message.from_user.id,
                         "Привет, тебя приветствует бот компании Too Easy Travel! Чем я могу помочь?")

    else:
        bot.send_message(message.from_user.id,
                         "Прости, не понимаю тебя. Попробуй написать снова или воспользуйся командами.")


bot.infinity_polling()
