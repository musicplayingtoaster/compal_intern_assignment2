from typing import Annotated
from fastapi import FastAPI, Form, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from . import database, postgre_database

class Todo(BaseModel):
    id: int | None = None
    todo: str
    resolved: int = 0

app = FastAPI()

@app.post("/submit")
async def create_todo(data: Annotated[Todo, Form()]):
    postgre_database.add_todo(data)
    return postgre_database.retrieve_latest_todo()

    # database.add_todo(data)
    # return database.retrieve_latest_todo()

@app.get("/load")
async def load_todos():
    print("retrieving todos")
    return postgre_database.retrieve_all_todos()

    # print("retrieving todos")
    # return database.retrieve_all_todos()

@app.delete("/delete")
async def delete_todo(id: Annotated[int, Body()]):
    postgre_database.remove_todo(id)
    # database.remove_todo(id)
    return "deleted"

@app.put("/update") # Note: "todo" is empty. this is just for transfering data for resolved
async def update_todo(data: Todo):
    postgre_database.update_todo(data.id, data.resolved)
    # database.update_todo(data.id, data.resolved)
    return "updated"

# app mount at the end, as if before the static file application will capture the request before the @app stuff does
# also you can't put this in main() ig... weird...
app.mount("/", StaticFiles(directory="src/assignment2/static", html=True), name="static")

def main() -> None:
    postgre_database.init_todo_list()
    # database.init_todo_list()
    uvicorn.run(app, host="0.0.0.0", port=3000) 

if __name__ == "__main__":
    main()