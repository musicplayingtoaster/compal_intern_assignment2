from pydantic import BaseModel
import psycopg2

# Adapt "database.py" code to run with Postgre instead
# Then make another service for database where Postgre will run on for "compose.yaml" (on Azure VM)

credentials = {
    "database": "todo_list_database",
}

def init_todo_list() -> None:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_list (
                    id SERIAL PRIMARY KEY,
                    todo TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0
                )
            ''')
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")


def retrieve_latest_todo() -> tuple:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM todo_list ORDER BY id DESC LIMIT 1")
            latest_row = cursor.fetchone()
            return latest_row
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def retrieve_all_todos() -> tuple:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM todo_list ORDER BY id")
            all_rows = cursor.fetchall()

            for row in all_rows:
                print(row)

            return all_rows
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def add_todo(todo:BaseModel) -> None:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO todo_list (todo) VALUES (%(todo)s)", todo.model_dump()) # resolved default value = 0
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def remove_todo(primary_key:int) -> tuple:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM todo_list WHERE id = %s", (primary_key,))
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def update_todo(primary_key:int, resolved:int) -> tuple:
    try:
        with psycopg2.connect(**credentials) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE todo_list SET resolved = %s WHERE id = %s", (resolved, primary_key,))
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")
