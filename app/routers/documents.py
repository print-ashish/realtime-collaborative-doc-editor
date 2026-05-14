import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..ot_engine import apply_operation
from typing import List

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=schemas.Document)
def create_document(doc: schemas.DocumentCreate, owner_id: int, db: Session = Depends(get_db)):
    # 1. Generate a unique string ID using uuid.uuid4()
    # Hint: str(uuid.uuid4())[:8] gives a nice short 8-char ID
    doc_id = str(uuid.uuid4())
    
    # 2. Create the document model
    new_doc = models.Document(
        id=doc_id,
        title=doc.title,
        owner_id=owner_id
    )
    
    # 3. Save to DB
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    new_doc.content = ""
    new_doc.revision = 0
    return new_doc

@router.get("/{doc_id}", response_model=schemas.Document)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    # Your code here
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code = 404, detail="Document not found")

    operations = db.query(models.Operation).filter(models.Operation.doc_id == doc_id).order_by(models.Operation.revision).all()

    #replay the history
    current_text = ""
    for op in operations:
        current_text = apply_operation(current_text , op.op_type , op.position , op.content)

    db_doc.content = current_text
    db_doc.revision = len(operations)
    return db_doc


@router.post("/{doc_id}/operations", response_model = schemas.Operation)
def create_operation(doc_id: str , op : schemas.OperationCreate , db : Session = Depends(get_db)):
    #lets check first the doc id exist or nto 
    db_doc = db.query(models.Document).filter(models.Document.id== doc_id).first()
    if not db_doc:
        raise HTTPException(status_code = 404 , detail = "Document not found")

    #count the total operatiions
    count = db.query(models.Operation).filter(models.Operation.doc_id == doc_id).count()
    next_revision = count + 1 

    new_op = models.Operation( 
        doc_id = doc_id, 
        user_id = op.user_id,
        op_type = op.op_type,
        position = op.position,
        content = op.content ,
         revision = next_revision
    )
    db.add(new_op)
    db.commit()
    db.refresh(new_op)
    return new_op

@router.get("/user/{user_id}", response_model=List[schemas.Document])
def get_user_documents(user_id: int, db: Session = Depends(get_db)):
    # 1. Fetch all documents owned by this user
    documents = db.query(models.Document).filter(models.Document.owner_id == user_id).all()
    
    # 2. Set default empty values so the schema doesn't complain
    for doc in documents:
        doc.content = ""
        doc.revision = 0
        
    return documents