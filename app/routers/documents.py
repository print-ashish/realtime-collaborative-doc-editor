import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

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
    return new_doc

@router.get("/{doc_id}", response_model=schemas.Document)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    # Your code here
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code = 404, detail="Document not found")
    return db_doc
