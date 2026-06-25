from typing import Annotated
from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
import uvicorn
from . import database, postgre_database, helper
import json

from psycopg import Connection, AsyncConnection
import redis
import redis.asyncio as aioredis



app = FastAPI(lifespan=helper.lifespan)

#@app.post("/submit")
async def create_todo(data: helper.Todo, conn_db: AsyncConnection, conn_cache: aioredis.Redis):
    # websocket to tell all clients new todo has been added and push change that way
    # do not return the retrieve

    #return postgre_database.retrieve_latest_todo()

    # database.add_todo(data)
    return await postgre_database.add_todo(data, conn_db, conn_cache)

@app.get("/load")
async def load_todos(conn_db: Connection = Depends(helper.get_pg_sync_conn), 
                     conn_cache: redis.Redis = Depends(helper.get_rdcache_sync_conn)):
    print("retrieving todos")
    return postgre_database.retrieve_all_todos(conn_db, conn_cache)

    # print("retrieving todos")
    # return database.retrieve_all_todos()

@app.delete("/delete")
async def delete_todo(id: Annotated[int, Body()], 
                      conn_db: Connection = Depends(helper.get_pg_sync_conn), 
                      conn_cache: redis.Redis = Depends(helper.get_rdcache_sync_conn)):
    postgre_database.remove_todo(id, conn_db, conn_cache)
    # database.remove_todo(id)
    return "deleted"

@app.put("/update") # Note: "todo" is empty. this is just for transfering data for resolved
async def update_todo(data: helper.Todo, 
                      conn_db: Connection = Depends(helper.get_pg_sync_conn), 
                      conn_cache: redis.Redis = Depends(helper.get_rdcache_sync_conn)):
    postgre_database.update_todo(data.id, data.resolved, conn_db, conn_cache)
    # database.update_todo(data.id, data.resolved)
    return "updated"


# Websocket stuff
manager = helper.ConnectionManager()

@app.websocket("/ws")
async def handle_websockets(websocket: WebSocket, 
                            channel:str = helper.CHANNEL_NAME, 
                            pubsub_client: aioredis.Redis = Depends(helper.get_rdpubsub_conn), 
                            conn_db: AsyncConnection = Depends(helper.get_pg_async_conn), 
                            conn_cache: aioredis.Redis = Depends(helper.get_rdcache_async_conn)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            recent = json.dumps(await create_todo(helper.Todo.model_validate(data), conn_db, conn_cache))
            
            # await manager.broadcast(recent)

            # publishes to channel -> move to helper.redis_listener to follow trail
            await pubsub_client.publish(channel, recent)
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
