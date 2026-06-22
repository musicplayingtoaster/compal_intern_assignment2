from pydantic import BaseModel
import psycopg
import os
from dotenv import load_dotenv

# Adapt "database.py" code to run with Postgre instead
# Then make another service for database where Postgre will run on for "compose.yaml" (on Azure VM)

load_dotenv()

connection_params = {
    "host": os.environ.get('DB_HOST'), 
    "port": os.environ.get('DB_PORT'),
    "dbname": os.environ.get('DB_DATABASE'),
    "user": os.environ.get('DB_USER'),
    "password": os.environ.get('DB_PASSWORD'),
}

def init_todo_list() -> None:
    try:
        with psycopg.connect(**connection_params) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_list (
                    id SERIAL PRIMARY KEY,
                    todo TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0
                )
            ''')
            connection.commit()
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")


async def retrieve_latest_todo() -> tuple:
    try:
        async with await psycopg.AsyncConnection.connect(**connection_params) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM todo_list ORDER BY id DESC LIMIT 1")
                latest_row = await cursor.fetchone()
                return latest_row
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def retrieve_all_todos() -> tuple:
    try:
        with psycopg.connect(**connection_params) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM todo_list ORDER BY id")
            all_rows = cursor.fetchall()

            for row in all_rows:
                print(row)

            return all_rows
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

async def add_todo(todo:BaseModel) -> tuple:
    try:
        async with await psycopg.AsyncConnection.connect(**connection_params) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO todo_list (todo) VALUES (%(todo)s)", todo.model_dump()) # resolved default value = 0
                await connection.commit()
                return await retrieve_latest_todo()
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def remove_todo(primary_key:int) -> tuple:
    try:
        with psycopg.connect(**connection_params) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM todo_list WHERE id = %s", (primary_key,))
            connection.commit()
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

def update_todo(primary_key:int, resolved:int) -> tuple:
    try:
        with psycopg.connect(**connection_params) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE todo_list SET resolved = %s WHERE id = %s", (resolved, primary_key,))
            connection.commit()
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")
