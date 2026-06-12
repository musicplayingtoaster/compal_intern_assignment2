from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import database

class Todo(BaseModel):
    id: int
    todo: str
    resolved: int

app = FastAPI()

# use a get to read what is currently in the database
# use a post to create a new todo
# use a delete to delete (wow no way)
# use a put to update its resolved status


@app.post("/create-todo/")
async def update_todo_list(todo: str):
    database.add_todo(todo)
    new_todo = database.retrieve_latest_todo()
    return {"todo": {new_todo[1]}, "resolved": {new_todo[2]}}


def main() -> None:
    database.init_todo_list()
    uvicorn.run(app, host="127.0.0.1", port=3000) 
    # change host to 0.0.0.0 when packaging for docker on azure vm