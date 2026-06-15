from typing import Annotated
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
#import database

class Todo(BaseModel):
    todo: str
    resolved: int = 0

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# use a get to read what is currently in the database
# use a post to create a new todo
# use a delete to delete (wow no way)
# use a put to update its resolved status

@app.post("/submit")
async def create_todo_(data: Annotated[Todo, Form()]):
    print("hit python")
    #database.add_todo(data)
    return data

@app.get("/")
def read_root():
    return FileResponse("static/index.html")


def main() -> None:
    #database.init_todo_list()
    uvicorn.run(app, host="0.0.0.0", port=3000) 

if __name__ == "__main__":
    main()