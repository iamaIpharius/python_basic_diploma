import sqlite3


def connect_to_db(db):
    return sqlite3.connect(db, check_same_thread=False)


def drop_table(value, cursor, connection):
    user = 'user' + str(value.chat.id)
    cursor.execute(f"DROP TABLE {user}")
    connection.commit()


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


def insert_row(value, cursor, connection):
    user = 'user' + str(value.chat.id)
    cursor.execute(f"INSERT INTO {user} VALUES ('{value.text}', '*', '*', '*', '*', '*', '*', '*', '*', '*')")
    connection.commit()


def update_db(value, column, cursor, connection):
    user = 'user' + str(value.chat.id)
    cursor.execute(
        f"""UPDATE {user} SET {column} = "{str(value.text)}" WHERE rowid = (SELECT MAX(rowid) FROM {user})""")
    connection.commit()


def fetch_db(value, cursor):
    user = 'user' + str(value.chat.id)
    cursor.execute(f"SELECT * FROM {user}")
    table = cursor.fetchall()
    work_row = table[-1]
    return work_row


def fetch_all_db(value, cursor):
    user = 'user' + str(value.chat.id)
    cursor.execute(f"SELECT * FROM {user}")
    table = cursor.fetchall()
    return table
