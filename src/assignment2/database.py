import sqlite3
from pydantic import BaseModel
'Deprecated: Moving to PostgreSQL'

'creates table in db if it doesnt already exist || item = todo item, resolved = done/not done'
'tuple order: [0=id,1=todo,2=resolved]'
def init_todo_list() -> None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_list (
                    id INTEGER PRIMARY KEY,
                    todo TEXT NOT NULL,
                    resolved INTEGER NOT NULL
                )
            ''')
            connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")


def retrieve_todo(todo:BaseModel) -> tuple:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT todo_id FROM todo_list WHERE todo = :todo", todo.model_dump())
            row = cursor.fetchone()
            if row:
                return row
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")


def retrieve_latest_todo() -> tuple:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM todo_list ORDER BY id DESC LIMIT 1")
            return cursor.fetchone()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def retrieve_all_todos() -> tuple:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM todo_list ORDER BY id")
            all_rows = cursor.fetchall()

            for row in all_rows:
                print(row)

            return all_rows
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def add_todo(todo:BaseModel) -> None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO todo_list (todo, resolved) VALUES (:todo, :resolved)", todo.model_dump())
            connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")



def remove_todo(primary_key:int) -> None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM todo_list WHERE id = ?", (primary_key,))
            connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def update_todo(primary_key:int, resolved:int) ->None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE todo_list SET resolved = ? WHERE id = ?", (resolved, primary_key,))
            connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")
