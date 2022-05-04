# Телеграм-бот для подбора отелей и хостелов

## Структура бота

##### **Сожержание Main.py**
---
**TOKEN** - Ваш токен бота

* **connection = db.connect_to_db('data.db')** -  соединение с базой данных
* **cursor = connection.cursor()** -  подключение курсора для управлениея базой данных
* **log_path = pathlib.PurePath(f"logs/main_log.log")** - создание пути для формирования лога
* **logger.add(log_path, format="{time} {level} {message}", level="INFO")** - подключение логгера


### В завистимости от входящего сообщения вызывается одна из стартовых функций:
* send_welcome(message: types.Message) Приветственное сообщение, ответ на команду start
* respond_to_help(message: types.Message) Ответ на команду help с перечнем команд для управления ботом
* lowprice_start(message: types.Message) Команда lowprice, запускает цепочку вопросов для поиска отелей по самой низкой цене, Пользователю задается вопрос "Куда едем?"
* highprice_start(message: types.Message) Команда highprice, запускает цепочку вопросов для поиска отелей по самой высокой цене, Пользователю задается вопрос "Куда едем?"
* bestdeal_start(message: types.Message) Команда bestdeal, запускает цепочку вопросов для поиска отелей по цены и расстояния до центра, Пользователю задается вопрос "Куда едем?"
* get_history(message: types.Message) Пользователю направляется история запросов

### Цепочка функций в основном одна, с различиями для bestdeal и разветвлением на запрос с фото и без фото:
* where_we_going(message: types.Message) второй шаг в цепочке, сюда поступает информация о городе назначения и добавляется в базу данных, Пользователю задается вопрос "Сколько отелей нужно найти?"
* how_many_hotels(message: types.Message): Следующий шаг, сюда поступает информация о количестве отелей, которые нужно вывести, и добавляется в базу данных, Далее задействуется модуль Календарь, у пользователя запрашиваются даты заезда и выезда
* def cal(call: types.CallbackQuery) Функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ, передает ответ в БД, и переходит к следующему шагу
* def set_check_in(chat_id: int) Функция вызова даты выезда
* def cal(call: types.CallbackQuery) Функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ, передает ответ в БД, и переходит к следующему шагу
* set_check_out(message: types.Message) Регистрируется следующий шаг в зависимости от ответа пользователя. Здесь начинается ветвление, если изначальна команда bestdeal то запрошивается минимальная цена в долларах и вызывается соответствующая функция min_price:
* min_price(message: types.Message): Фиксирует информацию о минимальной сумме, Пользователю задается вопрос "Максимальная сумма в долларах?" 
* max_price(message: types.Message): Фиксирует информацию о максимальной сумме, Пользователю задается вопрос "Минимальная дистанция от центра в км?" 
* min_distance(message: types.Message): Фиксирует информацию о минимальном расстоянии, Пользователю задается вопрос "Максимальная дистанция от центра в км?"
* max_distance(message: types.Message): Фиксирует информацию о максимальном расстоянии, далее цепочка возвращается в обычно русло и Пользователю задается вопрос "Нужны ли фото? да/нет"

### Если фото не нужны 
* need_photos(message: types.Message) Сохраняет значение Нет и заканчивает цепочку запросов, вызывает функции для получения результата
### Результат без фото
* work_row = db.fetch_db(message, cursor) формируется рабочая строка из информации добавленной в базу данных
* dest_id = commands.get_destination_id(work_row[1]) - Используя HotelsAPI определсяется ID места назначения
* current_hotels_list = commands.hotels_list_bestdeal - формируется список отелей с помощью HotelsAPI, подходящих под заданные параметры

**Далее с помощью цикла проходимся по найденным отелям и формируем из каждого итоговое сообщение для отправки в чат и отправляем. Также записываем во вторую базу данных для храниения истории - history**



        if current_hotels_list: - Если список существует (нашлись отели)
            for hotel in current_hotels_list: Цикл
                current_time = datetime.datetime.now() Время формирования сообщения
                db.insert_history_row(message, work_row[0], current_time.strftime("%d-%m-%Y %H:%M"), hotel['name'],
                                        cursor,
                                        connection) - База данных истории

                info_about_hotel = commands.form_result_string(hotel) - Формируем итоговое сообщение
                bot.send_message(message.chat.id, info_about_hotel) - Отправляем итоговое сообщение
        else:
            bot.send_message(message.chat.id, "К сожалению отелей не найдено") - Список не существует, отелей не найдено

### Если фотографии нужны  
* need_photos(message: types.Message) вызывает следующую функцию, сохраняет в базу данных информацию о том, что фото нужны, Пользователю задается вопрос "Сколько фото нужно?"
* how_many_photos(message: types.Message) Сохраняет в базу данных количество фотографий и заканчивает цепочку сбора информации, вызывает функции для получения результата
### Результат c фото
* work_row = db.fetch_db(message, cursor) формируется рабочая строка из информации добавленной в базу данных
* dest_id = commands.get_destination_id(work_row[1]) - Используя HotelsAPI определсяется ID места назначения
* current_hotels_list = commands.hotels_list_bestdeal - формируется список отелей с помощью HotelsAPI, подходящих под заданные параметры

**Далее с помощью цикла проходимся по найденным отелям и формируем из каждого итоговое сообщение для отправки в чат и отправляем. Также записываем во вторую базу данных для храниения истории - history**

        if current_hotels_list: Если список существует (нашлись отели)
            for hotel in current_hotels_list: Цикл
                current_time = datetime.datetime.now() Время формирования сообщения
                db.insert_history_row(message, work_row[0], current_time.strftime("%d-%m-%Y %H:%M"), hotel['name'],
                                      cursor,
                                      connection) - База данных истории

                info_about_hotel = commands.form_result_string(hotel) Формируем итоговое сообщение
                current_photos_list = commands.get_photos(hotel['id']) формируем список фото
                current_photos_list = [x.format(size='b') for x in current_photos_list] Приводим список фото в подходящий формат
                media_array = [InputMediaPhoto(x) for x in current_photos_list[:int(message.text)]] Формируем медиагруппу, используя заданное ранее количество фотографий message.text
                media_array[0].caption = info_about_hotel Добавляем в медиагруппу итоговое сообщение
                bot.send_media_group(message.chat.id, media_array) направляем пользователю
        else:
            bot.send_message(message.chat.id, "К сожалению отелей не найдено")  - Список не существует, отелей не найдено




* get_text_messages(message: types.Message): - Отвечает на любой другой текст кроме комманд

##### **Модуль Database**
---
**Используется SQLite3**

* connect_to_db: Функция для соединения с базой данных

        def connect_to_db(db):
            return sqlite3.connect(db, check_same_thread=False)

* drop_table: Функция для удаления таблицы

        def drop_table(value, cursor, connection):
            user = 'user' + str(value.chat.id)
            cursor.execute(f"DROP TABLE {user}")
            connection.commit()

* create_table_if_not_exists: Создание таблицы пользователя в базе данных

        def create_table_if_not_exists(value, cursor, connection):
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

* create_table_history_if_not_exists: Создание таблицы истории пользователя в базе данных

        def create_table_history_if_not_exists(value, cursor, connection):
            user = 'user' + str(value.chat.id) + 'history'
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user} (
                command text, 
                time text,
                hotel_name text
                )""")
            connection.commit()

* insert_row: Добавить строку в таблицу. Строка соответствует новому запросу

        def insert_row(value, cursor, connection):
            user = 'user' + str(value.chat.id)
            cursor.execute(f"INSERT INTO {user} VALUES ('{value.text}', '*', '*', '*', '*', '*', '*', '*', '*', '*')")
            connection.commit()

* insert_history_row: Добавить строку в таблицу истории. Строка соответствует каждому полученному отелю

        def insert_history_row(value, command, time, hotel_name, cursor, connection):
            user = 'user' + str(value.chat.id) + 'history'
            cursor.execute(f"INSERT INTO {user} VALUES ('{command}', '{str(time)}', '{hotel_name}')")
            connection.commit()

* update_db: Обновить таблицу, добавив новые данные

        def update_db(value, column, cursor, connection):
            user = 'user' + str(value.chat.id)
            cursor.execute(
                f"""UPDATE {user} SET {column} = "{str(value.text)}" 
                WHERE rowid = (SELECT MAX(rowid) FROM {user})""")
            connection.commit()

* fetch_db: Выгрузить из таблицы последнюю строку

        def fetch_db(value, cursor):
            user = 'user' + str(value.chat.id)
            cursor.execute(f"SELECT * FROM {user}")
            table = cursor.fetchall()
            work_row = table[-1]
            return work_row

* fetch_all_db: Выгрузить всю таблицу. Если нужно выгрузить всю таблицу из истории - устанавливаея флаг True. Иначе выгружается вся таблица для работы с отелями.

        def fetch_all_db(value, cursor, is_history=False):
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

##### **Модуль Commands**
---




## Использование бота в Телеграмм
### Команды
1. **/start** - запуск бота, возвращает смайлик
2. **/hellowrold** - команада возвращает "Hello, World!"

### Фразы, на которые реагирует бот
1. **Привет** - ответ бота "Привет, тебя приветствует бот компании Too Easy Travel! Чем я могу помочь?"

### Если запрос не распознан ботом
1. "Прости, не понимаю тебя. Попробуй написать снова или воспользуйся командами."
