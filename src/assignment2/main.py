from typing import Annotated
from fastapi import FastAPI, Form
from pydantic import BaseModel
import uvicorn
import database

class Todo(BaseModel):
    todo: str
    resolved: int = 0

app = FastAPI()

# use a get to read what is currently in the database
# use a post to create a new todo
# use a delete to delete (wow no way)
# use a put to update its resolved status

@app.post("/submit")
async def create_todo_(data: Annotated[Todo, Form()]):
    print("hit python")
    database.add_todo(data)
    return data
    


def main() -> None:
    database.init_todo_list()
    uvicorn.run(app, host="127.0.0.1", port=3000) 
    # change host to 0.0.0.0 when packaging for docker on azure vm