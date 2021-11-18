import sqlite3


def create_table_if_not_exists(value, cursor, connection):
    user = 'user' + str(value.from_user.id)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user} (
        command text,
        city text,
        hotels_count text,
        check_in text,
        check_out text,
        photos text
        )""")
    connection.commit()


def insert_row(value, cursor, connection):
    user = 'user' + str(value.from_user.id)
    cursor.execute(f"INSERT INTO {user} VALUES ('{value.text}', '*', '*', '*', '*', '*')")
    connection.commit()


def update_db(value, column, cursor, connection):
    user = 'user' + str(value.from_user.id)
    cursor.execute(
        f"""UPDATE {user} SET {column} = "{str(value.text)}" WHERE rowid = (SELECT MAX(rowid) FROM {user})""")
    connection.commit()


def fetch_db(value, cursor):
    user = 'user' + str(value.from_user.id)
    cursor.execute(f"SELECT * FROM {user}")
    table = cursor.fetchall()
    work_row = table[-1]
    print(work_row)
    return work_row