from .models import Todo
import psycopg
import os
import redis
from redis.exceptions import RedisError
import redis.asyncio as aioredis
from dotenv import load_dotenv
import re

# I might need to change this name now that redis is in here

load_dotenv()

CACHETTL = 300
latest_cache_key:str = None

connection_params_db = {
    "host": os.environ.get('DB_HOST'), 
    "port": os.environ.get('DB_PORT'),
    "dbname": os.environ.get('DB_DATABASE'),
    "user": os.environ.get('DB_USER'),
    "password": os.environ.get('DB_PASSWORD'),
}

connection_params_cache = {
    "host": os.environ.get('RDC_HOST'),
    "port": os.environ.get('RDC_PORT'),
    "db": 0,
    "decode_responses": True,
}

def init_todo_list() -> None:
    try:
        with psycopg.connect(**connection_params_db) as connection_db:
            cursor = connection_db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_list (
                    id SERIAL PRIMARY KEY,
                    todo TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0
                )
            ''')
            connection_db.commit()
    except psycopg.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")


async def retrieve_latest_todo() -> tuple:
    try:
        global latest_cache_key
        if latest_cache_key != None:
            async with aioredis.Redis(**connection_params_cache) as connection_cache:
                todo = await connection_cache.get(latest_cache_key)
                print("retrieved from cache!")
                if todo != None:
                    return tuple(Todo.model_validate_json(todo).model_dump().values())
        
        async with await psycopg.AsyncConnection.connect(**connection_params_db) as connection_db:
            async with connection_db.cursor() as cursor:
                await cursor.execute("SELECT * FROM todo_list ORDER BY id DESC LIMIT 1")
                latest_row = await cursor.fetchone()
                print("retrieved from db!")
                if latest_row != None:
                    return latest_row
        
    except (psycopg.OperationalError, RedisError) as e:
        print("Failed to open database and/or cache:", e)

def get_numeric_sort_key(key):
    match = re.search(r'\d+', key[5:])
    return int(match.group()) if match else 0

def retrieve_all_todos() -> tuple:
    try:
        todos = []
        cached_primary_keys = []
        with redis.Redis(**connection_params_cache) as connection_cache:
            unordered_keys = list(connection_cache.scan_iter(match='todo:*'))
            sorted_keys = sorted(unordered_keys, key=get_numeric_sort_key)

            pipeline = connection_cache.pipeline()
            for key in sorted_keys:
                pipeline.get(key)
            cached_values = pipeline.execute()

            for key, raw_json in zip(sorted_keys, cached_values):
                if not raw_json:
                    continue
                try:
                    todos.append(tuple(Todo.model_validate_json(connection_cache.get(key)).model_dump().values()))
                    cached_primary_keys.append(re.sub(r'\D+', '', key[5:]))
                except Exception:
                    continue
            
            print(f"retrieved from cache: {cached_primary_keys}")

        with psycopg.connect(**connection_params_db) as connection_db:
            cursor = connection_db.cursor()
            cursor.execute("SELECT * FROM todo_list WHERE id != ALL(%s)ORDER BY id", (cached_primary_keys,))
            all_rows = cursor.fetchall()
            todos = all_rows + todos

        print(todos)
        return todos
    except psycopg.OperationalError as e:
        print("Failed to open database and/or cache:", e, "(in short, you failed lmao.)")

async def add_todo(todo:Todo) -> tuple:
    try:
        async with await psycopg.AsyncConnection.connect(**connection_params_db) as connection_db, aioredis.Redis(**connection_params_cache) as connection_cache:
            async with connection_db.cursor() as cursor:
                await cursor.execute("INSERT INTO todo_list (todo) VALUES (%(todo)s) RETURNING id", todo.model_dump()) # resolved default value = 0
                await connection_db.commit()

                global latest_cache_key
                primary_key = await cursor.fetchone()
                latest_cache_key = f"todo:{primary_key[0]}"
                todo.id = primary_key[0]
                await connection_cache.setex(latest_cache_key, CACHETTL, todo.model_dump_json()) 

                return await retrieve_latest_todo()
    except psycopg.OperationalError as e:
        print("Failed to open database and/or cache:", e, "(in short, you failed lmao.)")

def remove_todo(primary_key:int) -> tuple:
    try:
        with psycopg.connect(**connection_params_db) as connection_db, redis.Redis(**connection_params_cache) as connection_cache:
            cursor = connection_db.cursor()
            cursor.execute("DELETE FROM todo_list WHERE id = %s", (primary_key,))
            connection_db.commit()

            connection_cache.delete(f"todo:{primary_key}")
    except psycopg.OperationalError as e:
        print("Failed to open database and/or cache:", e, "(in short, you failed lmao.)")

def update_todo(primary_key:int, _resolved:int) -> tuple:
    try:
        with psycopg.connect(**connection_params_db) as connection_db, redis.Redis(**connection_params_cache) as connection_cache:
            cursor = connection_db.cursor()
            cursor.execute("UPDATE todo_list SET resolved = %s WHERE id = %s RETURNING todo", (_resolved, primary_key,))
            connection_db.commit()

            updated_todo = cursor.fetchone()
            connection_cache.setex(f"todo:{primary_key}", CACHETTL, Todo(id=primary_key, todo=updated_todo[0], resolved=_resolved).model_dump_json())
    except psycopg.OperationalError as e:
        print("Failed to open database and/or cache:", e, "(in short, you failed lmao.)")
