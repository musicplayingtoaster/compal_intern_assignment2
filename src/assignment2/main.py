from typing import Annotated
from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from .helper import Todo, ConnectionManager
import uvicorn
from . import database, postgre_database
import json



app = FastAPI()

@app.post("/submit")
async def create_todo(data: Todo):
    # websocket to tell all clients new todo has been added and push change that way
    # do not return the retrieve

    #return postgre_database.retrieve_latest_todo()

    # database.add_todo(data)
    return await postgre_database.add_todo(data)

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


# Websocket stuff
manager = ConnectionManager()

@app.websocket("/ws")
async def handle_websockets(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            recent = await create_todo(Todo.model_validate(data))
            await manager.broadcast(json.dumps(recent))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# app mount at the end, as if before the static file application will capture the request before the @app stuff does
# also you can't put this in main() ig... weird...
app.mount("/", StaticFiles(directory="src/assignment2/static", html=True), name="static")

def main() -> None:
    postgre_database.init_todo_list()
    # database.init_todo_list()
    uvicorn.run(app, host="0.0.0.0", port=8000) 

if __name__ == "__main__":
    main()
