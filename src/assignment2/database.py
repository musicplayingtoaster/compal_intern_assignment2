# databaaaaaase
# i dont know what im doing but yea wahahahaha
import sqlite3

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


def retrieve_todo(todo:str) -> tuple:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT todo_id FROM todo_list WHERE todo = ?", todo)
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
            

def add_todo(todo:str) -> None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO todo (todo, resolved) VALUES (?, 0)", todo)
            connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")



def remove_todo(todo:str) -> None:
    try:
        with sqlite3.connect("todo_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT todo_id FROM todo_list WHERE todo = ?", todo)
            row = cursor.fetchone()

            if row:
                primary_key = row[0]
                cursor.execute("DELETE FROM todo_list WHERE id = ?", primary_key)
                connection.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")
