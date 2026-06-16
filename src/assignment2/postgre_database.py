from pydantic import BaseModel
import psycopg2

# Adapt "database.py" code to run with Postgre instead
# Then make another service for database where Postgre will run on for "compose.yaml" (on Azure VM)