from app.ot_engine import apply_operation
from fastapi import APIRouter , WebSocket , WebSocketDisconnect
from ..connection_manager import manager 
from ..database import SessionLocal
from ..import models , schemas
from fastapi.encoders import jsonable_encoder



router = APIRouter(tags=['websockets'])

@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket : WebSocket , document_id : str):
    await manager.connect(websocket , document_id)
    db = SessionLocal()

    try:
        while True:  
            data = await websocket.receive_json()
            
            # 1. Parse the incoming data
            op_data = schemas.OperationCreate(**data)

            # 2. Calculate next revision
            count = db.query(models.Operation).filter(models.Operation.doc_id == document_id).count()
            
            # 3. Save to DB
            new_op = models.Operation(
                doc_id=document_id,
                user_id=op_data.user_id,
                op_type=op_data.op_type,
                position=op_data.position,
                content=op_data.content,
                revision=count + 1
            )
            db.add(new_op)
            db.commit()
            db.refresh(new_op)

            # 4. Broadcast ONLY the new operation
            # Convert the DB model to a dictionary to send it
            broadcast_msg = jsonable_encoder(new_op) 

            # broadcast_msg = schemas.Operation.from_orm(new_op).dict()
            await manager.publish(document_id, broadcast_msg)
    except WebSocketDisconnect :
        manager.disconnect(websocket , document_id)