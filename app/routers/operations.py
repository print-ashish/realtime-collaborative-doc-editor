from app.ot_engine import apply_operation
from fastapi import APIRouter , WebSocket , WebSocketDisconnect
from ..connection_manager import manager 
from ..database import SessionLocal
from ..import models , schemas
from fastapi.encoders import jsonable_encoder
from ..ot_engine import transform_against_history
import asyncio





router = APIRouter(tags=['websockets'])

@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket : WebSocket , document_id : str):
    await manager.connect(websocket , document_id)
    db = SessionLocal()
    


    try:
        while True:  
            data = await websocket.receive_json()
            if data.get("type") == "cursor":
    # Just broadcast, don't save to DB
                await manager.publish(document_id, data)
                continue 
            # await asyncio.sleep(3)
            
            # 1. Parse the incoming data
            op_data = schemas.OperationCreate(**data)

            # 2. Calculate next revision
            count = db.query(models.Operation).filter(models.Operation.doc_id == document_id).count()
            
            # --- START OT ENGINE ---
            final_op_dict = op_data.dict()
            
            if op_data.revision < count:
                # User is behind! Fetch the "Gap" operations
                history = db.query(models.Operation).filter(
                    models.Operation.doc_id == document_id,
                    models.Operation.revision > op_data.revision
                ).order_by(models.Operation.revision.asc()).all()
            
            # Transform our new op against the history
                final_op_dict = transform_against_history(final_op_dict, history)
        # --- END OT ENGINE ---
        # 3. Save the (possibly transformed) operation
            new_op = models.Operation(
                doc_id=document_id,
                user_id=final_op_dict["user_id"],
                op_type=final_op_dict["op_type"],
                position=final_op_dict["position"],
                content=final_op_dict["content"],
                revision=count + 1
            )
            db.add(new_op)
            db.commit()
            await manager.publish(document_id ,{"type" : "status" , "msg"  : "Saved !"})
            db.refresh(new_op)

            # 4. Broadcast ONLY the new operation
            # Convert the DB model to a dictionary to send it
            broadcast_msg = jsonable_encoder(new_op) 

            # broadcast_msg = schemas.Operation.from_orm(new_op).dict()
            await manager.publish(document_id, broadcast_msg)
    except WebSocketDisconnect :
        manager.disconnect(websocket , document_id)