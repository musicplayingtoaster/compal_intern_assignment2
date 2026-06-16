from pydantic import BaseModel
import psycopg2

# Adapt "database.py" code to run with Postgre instead
# Then make another service for database where Postgre will run on for "compose.yaml" (on Azure VM)

DATABASE = ""
USER = ""
PASSWORD = ""

# if a login sequence is required
def login():
    pass

def init_todo_list() -> None:
    try:
        with psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todo_list (
                    id serial PRIMARY KEY,
                    todo varchar NOT NULL,
                    resolved integer NOT NULL
                )
            ''') 
            # While PostgreSQL has a boolean type, i just don't want to refactor the rest of the code cuz im lazy
            # sorry.
            
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")

# copy from here
def retrieve_latest_todo() -> tuple:
    try:
        with psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD) as connection:
            cursor = connection.cursor()
            cursor.execute()
            
            connection.commit()
    except psycopg2.OperationalError as e:
        print("Failed to open database:", e, "(in short, you failed lmao.)")