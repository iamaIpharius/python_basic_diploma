import sqlite3


def connect_to_db(db):
    """
    Соединение с базой данных
    :param db: имя базы данных
    :return: соединение
    """
    return sqlite3.connect(db, check_same_thread=False)


def drop_table(value, cursor, connection):
    """
    Удаление таблицы из базы данных
    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных
    """
    user = 'user' + str(value.chat.id)
    cursor.execute(f"DROP TABLE {user}")
    connection.commit()


def create_table_if_not_exists(value, cursor, connection):
    """
    Создание таблицы в базе данных, если еще не создана
    Для каждого пользователя создается уникальная таблица

    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных


    Таблица содержит следующие столбцы:
    command: Команда,
    city: Город посика,
    hotels_count: количество отелей,
    check_in: дата заезда,
    check_out: дата выезда,
    photos: нужны ли фото, да/нет,
    min_price: минимальная цена отеля,
    max_price: максимальная цена отеля,
    min_distance: минимальная дистанция до центра,
    max_distance: максимальная дистанция до центра
    """

    user = 'user' + str(value.chat.id)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user} (
        command text, 
        city text,
        hotels_count text,
        check_in text,
        check_out text,
        photos text,
        min_price text,
        max_price text,
        min_distance text,
        max_distance text
        )""")
    connection.commit()


def create_table_history_if_not_exists(value, cursor, connection):
    """
    Создание таблицы истории в базе данных, если еще не создана
    Для каждого пользователя создается уникальная таблица

    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных


    command: команда,
    time: дата и время,
    hotel_name: название отеля
    """
    user = 'user' + str(value.chat.id) + 'history'
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user} (
        command text, 
        time text,
        hotel_name text
        )""")
    connection.commit()


def insert_row(value, cursor, connection):
    """
    Вставить строку в таблицу
    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных
    """
    user = 'user' + str(value.chat.id)
    cursor.execute(f"INSERT INTO {user} VALUES ('{value.text}', '*', '*', '*', '*', '*', '*', '*', '*', '*')")
    connection.commit()


def insert_history_row(value, command, time, hotel_name, cursor, connection):
    """
    Вставить строку в таблицу истории
    :param value: сообщение пользователя, из которого берется chat.id
    :param command: команда
    :param time: дата и время
    :param hotel_name: название отеля
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных
    """
    user = 'user' + str(value.chat.id) + 'history'
    cursor.execute(f"INSERT INTO {user} VALUES ('{command}', '{str(time)}', '{hotel_name}')")
    connection.commit()


def update_db(value, column, cursor, connection):
    """
    Обновить последнюю строку в таблице (текущую). обновляется один параметр в строке
    :param value: сообщение пользователя, из которого берется chat.id
    :param column: название обновляемого столбца
    :param cursor: курсор для управления базой данных
    :param connection: соединение с базой данных
    """
    user = 'user' + str(value.chat.id)
    cursor.execute(
        f"""UPDATE {user} SET {column} = "{str(value.text)}" WHERE rowid = (SELECT MAX(rowid) FROM {user})""")
    connection.commit()


def fetch_db(value, cursor) -> tuple:
    """
    Выгрузить последнюю строку
    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :return: кортеж с данными из таблицы
    """
    user = 'user' + str(value.chat.id)
    cursor.execute(f"SELECT * FROM {user}")
    table = cursor.fetchall()
    work_row = table[-1]
    return work_row


def fetch_all_db(value, cursor, is_history=False) -> tuple:
    """
    Выгрузить всю таблицу, может использоваться дял выгрузки обоих видов таблиц в завистимости от флага is_history
    :param value: сообщение пользователя, из которого берется chat.id
    :param cursor: курсор для управления базой данных
    :param is_history: флаг для определения какую таблицу выгрузить, с историей или нет
    :return: кортеж с кортежами данных строк из таблицы
    """
    if is_history:
        user = 'user' + str(value.chat.id) + 'history'
        cursor.execute(f"SELECT * FROM {user}")
        table = cursor.fetchall()
        return table
    else:
        user = 'user' + str(value.chat.id)
        cursor.execute(f"SELECT * FROM {user}")
        table = cursor.fetchall()
        return table
