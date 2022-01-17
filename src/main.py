import telebot
from decouple import config
from telebot.types import InputMediaPhoto
from database import database as db
from botrequests import commands

TOKEN = config('TOKEN')

bot = telebot.TeleBot(TOKEN)

conn = db.connect_to_db('history.db')
c = conn.cursor()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    db.create_table_if_not_exists(message, c, conn)
    bot.reply_to(message, "( ͡° ͜ʖ ͡°)")


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, """
    Для управления мной есть такие команды:
    /lowprice - показать отели с самыми низкими ценами
    /highprice - показать самые дороги отели в городе
    /bestdeal - лучшее соотношение цены и близости к центру
    /history - история поиска отелей
    """)


@bot.message_handler(commands=['lowprice'])
def lowprice_start(message):
    db.insert_row(message, c, conn)

    bot.send_message(message.from_user.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(message, where_we_going)

@bot.message_handler(commands=['highprice'])
def highprice_start(message):
    db.insert_row(message, c, conn)

    bot.send_message(message.from_user.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(message, where_we_going)


def where_we_going(message):
    db.update_db(message, 'city', c, conn)

    bot.send_message(message.from_user.id, 'Сколько отелей нужно вывести в поиске? ')
    bot.register_next_step_handler(message, how_many_hotels)


def how_many_hotels(message):
    db.update_db(message, 'hotels_count', c, conn)

    bot.send_message(message.from_user.id, 'Дата заезда в формате yyyy-MM-dd: ')
    bot.register_next_step_handler(message, set_check_in)


def set_check_in(message):
    db.update_db(message, 'check_in', c, conn)

    bot.send_message(message.from_user.id, 'Дата выезда в формате yyyy-MM-dd: ')
    bot.register_next_step_handler(message, set_check_out)


def set_check_out(message):
    db.update_db(message, 'check_out', c, conn)

    bot.send_message(message.from_user.id, 'Нужны ли фотографии? (да/нет) ')
    bot.register_next_step_handler(message, need_photos)


def need_photos(message):
    db.update_db(message, 'photos', c, conn)

    bot.send_message(message.from_user.id, 'ОБРАБАТЫВАЮ...')

    work_row = db.fetch_db(message, c)

    if message.text.lower() == "да":
        bot.send_message(message.from_user.id, 'ИЩУ ФОТО...')
        dest_id = commands.get_destination_id(work_row[1])
        current_hotels_list = commands.hotels_list_by(dest_id, work_row[2], work_row[3], work_row[4], work_row[0])
        for hotel in current_hotels_list:
            info_about_hotel = commands.form_result_string(hotel)
            current_photos_list = commands.get_photos(hotel['id'])
            current_photos_list = [x.format(size='b') for x in current_photos_list]
            media_array = [InputMediaPhoto(x) for x in current_photos_list[:9]]
            media_array[0].caption = info_about_hotel
            bot.send_media_group(message.from_user.id, media_array)

    else:
        bot.send_message(message.from_user.id, 'ПОДОЖДИТЕ...')
        dest_id = commands.get_destination_id(work_row[1])
        current_hotels_list = commands.hotels_list_by(dest_id, work_row[2], work_row[3], work_row[4], work_row[0])
        for hotel in current_hotels_list:
            info_about_hotel = commands.form_result_string(hotel)
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
