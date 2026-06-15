from typing import Annotated
from fastapi import FastAPI, Form, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from . import database

class Todo(BaseModel):
    id: int | None = None
    todo: str
    resolved: int = 0

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/assignment2/static", html=True), name="static")

# use a get to read what is currently in the database
# use a post to create a new todo
# use a delete to delete (wow no way)
# use a put to update its resolved status

#data: Annotated[Todo, Form()]
@app.post("/submit")
async def create_todo(data: Annotated[Todo, Form()]):
    database.add_todo(data)
    return database.retrieve_latest_todo()

@app.get("/load")
async def load_todos():
    print("retrieving todos")
    return database.retrieve_all_todos()

@app.delete("/delete")
async def delete_todo(id: Annotated[int, Body()]):
    print("delete?")
    database.remove_todo(id)
    print("probably deleted")
    return "deleted"

@app.put("/update") # Note: "todo" is empty. this is just for transfering data for resolved
async def update_todo(data: Todo):
    print("update?")
    database.update_todo(data.id, data.resolved)
    print("probably updated")
    return "updated"


def main() -> None:
    database.init_todo_list()
    uvicorn.run(app, host="0.0.0.0", port=3000) 

if __name__ == "__main__":
    main()