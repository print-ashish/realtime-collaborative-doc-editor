from redis.commands import json
from app.routers import documents
from typing import List , Dict 
from fastapi import WebSocket
import json
import asyncio
from .redis_client import redis_client


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis_tasks : Dict[str , asyncio.Task] = {}



    async def connect(self, websocket: WebSocket , document_id : str ):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
            self.redis_tasks[document_id] = asyncio.create_task(self._redis_listener(document_id))

            
        self.active_connections[document_id].append(websocket) 

        

    def disconnect(self, websocket: WebSocket , document_id : str):
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                self.redis_tasks[document_id].cancel()
                del self.redis_tasks[document_id]
                del self.active_connections[document_id]

    async def publish(self, document_id : str , message: dict):
        await redis_client.publish(f"doc_{document_id}" , json.dumps(message))

    async def _redis_listener(self, document_id : str):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"doc_{document_id}")

        try: 
            async for message in pubsub.listen():
                if message["type"]== "message":
                    data = json.loads(message["data"])
                    await self._broadcast_local(data , document_id)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(f"doc_{document_id}")


    async def _broadcast_local(self ,  message : dict , document_id : str):
        if document_id in self.active_connections:
            for websocket in self.active_connections[document_id]:
                await websocket.send_json(message)



manager = ConnectionManager()