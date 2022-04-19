import telebot
from decouple import config
from telebot.types import InputMediaPhoto
from database import database as db
from botrequests import commands
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
from telebot import types
from loguru import logger
import pathlib
import re

TOKEN = config('TOKEN')

bot = telebot.TeleBot(TOKEN)

connection = db.connect_to_db('data.db')  # соединение с базой данных
cursor = connection.cursor()  # подключение курсора для управлениея базой данных


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    """
    Приветственное сообщение, ответ на команду start
    Создается таблица базы данных
    :param message:
    :return:
    """

    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")

    logger.info(f"{message.text}")
    # db.drop_table(message, cursor, connection)
    # connection.close()
    db.create_table_if_not_exists(message, cursor, connection)
    bot.reply_to(message, """
    Привет! Это бот для поиска отелей!
    Для управления мной есть такие команды:
    /lowprice - показать отели с самыми низкими ценами
    /highprice - показать самые дороги отели в городе
    /bestdeal - лучшее соотношение цены и близости к центру
    /history - история поиска отелей
    """)


@bot.message_handler(commands=['help'])
def send_welcome(message: types.Message):
    """
    Ответ на команду help с перечнем команд для управления ботом
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")
    bot.reply_to(message, """
    Для управления мной есть такие команды:
    /lowprice - показать отели с самыми низкими ценами
    /highprice - показать самые дороги отели в городе
    /bestdeal - лучшее соотношение цены и близости к центру
    /history - история поиска отелей
    """)


@bot.message_handler(commands=['lowprice'])
def lowprice_start(message: types.Message):
    """
    Команда lowprice, запускает цепочку вопрос дял поиска отелей по самой низкой цене
    в таблицу базы данных добавляется новая строка строка (весь запрос), которая будет дополняться

    бут задает вопрос и ответ пользователя передается в следующую по цепочке функцию и там регистрируется
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")
    db.insert_row(message, cursor, connection)

    mes = bot.send_message(message.chat.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(mes, where_we_going)


@bot.message_handler(commands=['highprice'])
def highprice_start(message: types.Message):
    """
    Команда highprice, запускает цепочку вопрос дял поиска отелей по самой высокой цене
    в таблицу базы данных добавляется новая строка строка (весь запрос), которая будет дополняться

    бут задает вопрос и ответ пользователя передается в следующую по цепочке функцию и там регистрируется
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")
    db.insert_row(message, cursor, connection)

    mes = bot.send_message(message.chat.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(mes, where_we_going)


@bot.message_handler(commands=['bestdeal'])
def bestdeal_start(message: types.Message):
    """
    Команда bestdeal, запускает цепочку вопрос дял поиска отелей по цены и расстояния до центра
    в таблицу базы данных добавляется новая строка строка (весь запрос), которая будет дополняться

    бут задает вопрос и ответ пользователя передается в следующую по цепочке функцию и там регистрируется
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")
    db.insert_row(message, cursor, connection)

    mes = bot.send_message(message.chat.id, 'Куда едем, командир? ')
    bot.register_next_step_handler(mes, where_we_going)


@bot.message_handler(commands=['history'])
def bestdeal_start(message: types.Message):
    """
    Из базы данных выгружается сырая информация в переменную history_table и затем с помощью функции form_history
    обрабатывается и затем из таблицы выводится история запросов (строк)
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")

    pattern = r"(\d{4}\-\d\d\-\d\d)\w(\d\d\:\d\d\:\d\d)(\.\d{6}\+\d{4})(.{,})"

    with open(f"logs/{str(message.chat.id)}_history.log", 'r', encoding="UTF-8") as history_file:
        result_string = 'Ваша история запросов:\n'
        for line in history_file:
            m = re.match(pattern, line)
            year = m.group(1)
            time = m.group(2)
            new_line = m.group(4)
            result_string = result_string + f"Время запроса: {year} {time},{new_line}\n"

        bot.send_message(message.chat.id, result_string)


def where_we_going(message: types.Message):
    """
    второй шаг в цепочке, сюда поступает информация о городе назначения и добавляется в строку таблицы
    Далее пользователю предлагают ответить на следующий вопрос и вызывается следующая по цепочке функция
    :param message:
    :return:
    """

    db.update_db(message, 'city', cursor, connection)
    logger.info(f"{message.text}")
    mes = bot.send_message(message.chat.id, 'Сколько отелей нужно вывести в поиске? ')

    bot.register_next_step_handler(mes, how_many_hotels)


def how_many_hotels(message: types.Message):
    """
    Следующий шаг, сбда поступает информация о количестве отелей, которые нужно вывести, и добавляется в строку таблицы.
    Далее задействуется модуль Календарь,  функция вызова даты въезда

    :param message:
    :return:
    """
    logger.info(f"{message.text}")
    db.update_db(message, 'hotels_count', cursor, connection)
    text = "Выберите дату заезда"
    bot.send_message(message.from_user.id, text)
    date = datetime.date.today()
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date).build()
    bot.send_message(message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    # bot.send_message(message.chat.id, 'Дата заезда в формате yyyy-MM-dd: ')
    # bot.register_next_step_handler(message, set_check_in)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call: types.CallbackQuery) -> None:
    """
    Функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ,
    передает ответ в БД,
    и переходит к следующему шагу
    :param call:запрос обраатного вызова с сообщением
    :return:
    """
    date = datetime.date.today()
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        call.message.text = str(result)

        db.update_db(call.message, 'check_in', cursor, connection)
        # bot.send_message(call.message.chat.id, call.message.text)
        logger.info(f"{call.message.text}")
        set_check_in(call.message.chat.id)


def set_check_in(chat_id: int) -> None:
    """
    Функция вызова даты выезда
    :param chat_id: ID чата
    :return:
    """
    date_today = datetime.date.today()
    text = "Выберите дату выезда"
    bot.send_message(chat_id, text)
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date_today).build()
    bot.send_message(chat_id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    # bot.send_message(message.chat.id, 'Дата выезда в формате yyyy-MM-dd: ')
    # bot.register_next_step_handler(message, set_check_out)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(call: types.CallbackQuery) -> None:
    """
    Функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ,
    передает ответ в БД,
    и переходит к следующему шагу
    :param call:запрос обратного вызова с сообщением
    """
    date_today = datetime.date.today()

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                 min_date=date_today).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        call.message.text = str(result)

        db.update_db(call.message, 'check_out', cursor, connection)
        # bot.register_next_step_handler(call.message, set_check_out)

        set_check_out(call.message)


def set_check_out(message: types.Message):
    """
    Регистрируется следующий шаг в зависимости от ответа пользователя
    :param message: сообщение от пользователя
    :return:
    """
    work_row = db.fetch_db(message, cursor)
    if work_row[0] == "/bestdeal":
        mes = bot.send_message(message.chat.id, 'Минимальная цена в долларах: ')
        logger.info(f"{message.text}")
        bot.register_next_step_handler(mes, min_price)

    else:
        mes = bot.send_message(message.chat.id, 'Нужны ли фотографии? (да/нет) ')
        logger.info(f"{message.text}")

        bot.register_next_step_handler(mes, need_photos)


def min_price(message: types.Message):
    db.update_db(message, 'min_price', cursor, connection)
    mes = bot.send_message(message.chat.id, 'Максимальная цена в долларах:  ')
    logger.info(f"{message.text}")
    bot.register_next_step_handler(mes, max_price)


def max_price(message: types.Message):
    db.update_db(message, 'max_price', cursor, connection)
    mes = bot.send_message(message.chat.id, 'Минимальное расстояние в километрах до центра:  ')
    logger.info(f"{message.text}")
    bot.register_next_step_handler(mes, min_distance)


def min_distance(message: types.Message):
    db.update_db(message, 'min_distance', cursor, connection)
    mes = bot.send_message(message.chat.id, 'Максимальное расстояние в километрах до центра:  ')
    logger.info(f"{message.text}")
    bot.register_next_step_handler(mes, max_distance)


def max_distance(message: types.Message):
    db.update_db(message, 'max_distance', cursor, connection)
    mes = bot.send_message(message.chat.id, 'Нужны ли фотографии? (да/нет) ')
    logger.info(f"{message.text}")

    bot.register_next_step_handler(mes, need_photos)


def need_photos(message: types.Message):
    """
    Регистрируется следующий шаг в зависимости от ответа пользователя
    если фото нужны - регистрируется дополнительный переход к функции how_many_photos

    если нет - строка бд обновляется и из строки базы данных формируется work_row, из которой в свою очередь извлекаются
    параметры для запроса в API и формирования итогового списка отелей
    Отели из списка по очереди направляются пользователю
    :param message: сообщение от пользователя
    :return:
    """

    logger.info(f"{message.text}")
    if message.text.lower() == "да":
        mes = bot.send_message(message.chat.id, 'Сколько фотографий? ')
        bot.register_next_step_handler(mes, how_many_photos)



    else:
        log_path_history = pathlib.PurePath(f"logs/{str(message.chat.id)}_history.log")
        logger.add(log_path_history, format="{time} {message}")

        db.update_db(message, 'photos', cursor, connection)

        bot.send_message(message.chat.id, 'ОБРАБАТЫВАЮ...')

        work_row = db.fetch_db(message, cursor)
        if work_row[0] == "/bestdeal":
            bot.send_message(message.chat.id, 'ПОДОЖДИТЕ...')
            dest_id = commands.get_destination_id(work_row[1])
            current_hotels_list = commands.hotels_list_bestdeal(dest_id, work_row[2], work_row[3], work_row[4],
                                                                work_row[0], work_row[6], work_row[7], work_row[8],
                                                                work_row[9])
            if current_hotels_list:
                for hotel in current_hotels_list:
                    logger.success(f"команда: {work_row[0]}, название отеля: {hotel['name']}")
                    info_about_hotel = commands.form_result_string(hotel)
                    bot.send_message(message.chat.id, info_about_hotel)
            else:
                bot.send_message(message.chat.id, "К сожалению отелей не найдено")
        else:
            bot.send_message(message.chat.id, 'ПОДОЖДИТЕ...')
            dest_id = commands.get_destination_id(work_row[1])
            current_hotels_list = commands.hotels_list_by(dest_id, work_row[2], work_row[3], work_row[4], work_row[0])
            if current_hotels_list:
                for hotel in current_hotels_list:
                    logger.success(f"команда: {work_row[0]}, название отеля: {hotel['name']}")
                    info_about_hotel = commands.form_result_string(hotel)
                    bot.send_message(message.chat.id, info_about_hotel)
            else:
                bot.send_message(message.chat.id, "К сожалению отелей не найдено")


def how_many_photos(message: types.Message):
    """
    Вызывается если нужны фоторафии
    Строка БД дополняется количетсвом фотографий
    строка бд обновляется и из строки базы данных формируется work_row, из которой в свою очередь извлекаются
    параметры для запроса в API и формирования итогового списка отелей
    Отели из списка по очереди направляются пользователю
    :param message:
    :return:
    """

    logger.info(f"{message.text}")
    db.update_db(message, 'photos', cursor, connection)
    bot.send_message(message.chat.id, 'ОБРАБАТЫВАЮ...')

    work_row = db.fetch_db(message, cursor)

    log_path_history = pathlib.PurePath(f"logs/{str(message.chat.id)}_history.log")
    logger.add(log_path_history, format="{time} {message}")

    if work_row[0] == "/bestdeal":
        bot.send_message(message.chat.id, 'ИЩУ ФОТО...')
        dest_id = commands.get_destination_id(work_row[1])
        current_hotels_list = commands.hotels_list_bestdeal(dest_id, work_row[2], work_row[3], work_row[4], work_row[0],
                                                            work_row[6], work_row[7], work_row[8], work_row[9])
        if current_hotels_list:
            for hotel in current_hotels_list:
                logger.success(f"команда: {work_row[0]}, название отеля: {hotel['name']}")
                info_about_hotel = commands.form_result_string(hotel)
                current_photos_list = commands.get_photos(hotel['id'])
                current_photos_list = [x.format(size='b') for x in current_photos_list]
                media_array = [InputMediaPhoto(x) for x in current_photos_list[:int(message.text)]]
                media_array[0].caption = info_about_hotel
                bot.send_media_group(message.chat.id, media_array)
        else:
            bot.send_message(message.chat.id, "К сожалению отелей не найдено")
    else:
        bot.send_message(message.chat.id, 'ИЩУ ФОТО...')
        dest_id = commands.get_destination_id(work_row[1])
        current_hotels_list = commands.hotels_list_by(dest_id, work_row[2], work_row[3], work_row[4], work_row[0])

        if current_hotels_list:
            for hotel in current_hotels_list:
                logger.success(f"команда: {work_row[0]}, название отеля: {hotel['name']}")
                info_about_hotel = commands.form_result_string(hotel)
                current_photos_list = commands.get_photos(hotel['id'])
                current_photos_list = [x.format(size='b') for x in current_photos_list]
                media_array = [InputMediaPhoto(x) for x in current_photos_list[:int(message.text)]]
                media_array[0].caption = info_about_hotel
                bot.send_media_group(message.chat.id, media_array)
        else:
            bot.send_message(message.chat.id, "К сожалению отелей не найдено")


@bot.message_handler(content_types=['text'])
def get_text_messages(message: types.Message):
    """
    Вызывается если пользовательский текст не подпадает под команды или ответы
    :param message:
    :return:
    """
    log_path = pathlib.PurePath(f"logs/{str(message.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}", level="INFO")
    logger.info(f"{message.text}")
    if 'привет' in message.text.lower():

        bot.send_message(message.chat.id,
                         "Привет, тебя приветствует бот компании Too Easy Travel! Чем я могу помочь?")

    else:
        bot.send_message(message.chat.id,
                         "Прости, не понимаю тебя. Попробуй написать снова или воспользуйся командами.")


bot.infinity_polling()
