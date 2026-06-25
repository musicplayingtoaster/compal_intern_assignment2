import os
import asyncio
import redis
import redis.asyncio as aioredis
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from psycopg import Connection, AsyncConnection
from psycopg_pool import ConnectionPool, AsyncConnectionPool
from typing import Generator, AsyncGenerator

# Helpful stuff here

class Todo(BaseModel):
    id: int | None = None
    todo: str
    resolved: int = 0

connection_params_db = {
    "host": os.environ.get('DB_HOST'), 
    "port": os.environ.get('DB_PORT'),
    "dbname": os.environ.get('DB_DATABASE'),
    "user": os.environ.get('DB_USER'),
    "password": os.environ.get('DB_PASSWORD'),
}

connection_params_redis = {
    "host": os.environ.get('RDC_HOST'),
    "port": os.environ.get('RDC_PORT'),
    "db": 0,
    "decode_responses": True,
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    # connection needs to be async as it requires waiting to ensure the websocket connection from client is successful
    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        print("connected:", websocket)
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, data):
        for connection in self.active_connections:
            try:
                print("attempting to send data:", data, "to ", connection)
                await connection.send_json(data)
            except Exception:
                pass

CHANNEL_NAME = "global_broadcast"
manager = ConnectionManager()
redispubsub_client: aioredis.Redis | None = None

async def redis_listener():
    if redispubsub_client == None:
        return
    
    async with redispubsub_client.pubsub() as pubsub:
        try:
            await pubsub.subscribe(CHANNEL_NAME)
            # hears published message back in main.py and then sends a websocket broadcast to client
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await manager.broadcast(message["data"])
        except asyncio.CancelledError:
            print("Redis listener cancelled")
        except Exception as e:
            print("Redis error:", e)

postgres_sync_pool: ConnectionPool = None
postgres_async_pool: AsyncConnectionPool = None
rediscache_sync_client: redis.Redis | None = None
rediscache_async_client: aioredis.Redis | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global postgres_sync_pool, postgres_async_pool, rediscache_sync_client, rediscache_async_client
    postgres_sync_pool = ConnectionPool(kwargs=connection_params_db, open=False)
    postgres_async_pool = AsyncConnectionPool(kwargs=connection_params_db, open=False)
    
    sync_pool = redis.ConnectionPool(**connection_params_redis)
    async_pool = aioredis.ConnectionPool(**connection_params_redis)
    pubsub_pool = aioredis.ConnectionPool(**connection_params_redis)

    rediscache_sync_client = redis.Redis(connection_pool=sync_pool)
    rediscache_async_client = aioredis.Redis(connection_pool=async_pool)
    redispubsub_client = aioredis.Redis(connection_pool=pubsub_pool)
    listener_task = asyncio.create_task(redis_listener())

    postgres_sync_pool.open()
    await postgres_async_pool.open()

    yield

    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass

    if postgres_sync_pool:
        postgres_sync_pool.close()
    if postgres_async_pool:
        await postgres_async_pool.close()
    if rediscache_sync_client:
        rediscache_sync_client.close()
    if rediscache_async_client:
        await rediscache_async_client.aclose()
    if redispubsub_client:
        await redispubsub_client.aclose()

# Stuff Down Here = Dependency Injection Functions
# Example for connection (conn: Connection = Depends(get_pg_sync_conn))
def get_pg_sync_conn() -> Generator[Connection, None, None]:
    with postgres_sync_pool.connection() as connection:
        yield connection

async def get_pg_async_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with postgres_async_pool.connection() as connection:
        yield connection

def get_rdcache_sync_conn() -> redis.Redis:
    if rediscache_sync_client is None:
        raise RuntimeError("Sync Redis Cache client is not initialized")
    return rediscache_sync_client

# Example again but for redis (async def get_value(key: str, redis: aioredis.Redis = Depends(get_redis)):)
async def get_rdcache_async_conn() -> aioredis.Redis:
    if rediscache_async_client is None:
        raise RuntimeError("Async Redis Cache client is not initialized")
    return rediscache_async_client

async def get_rdpubsub_conn() -> aioredis.Redis:
    if redispubsub_client is None:
        raise RuntimeError("Redis PubSub client is not initialized")
    return redispubsub_client