from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OperationBase(BaseModel):
    doc_id: str
    op_type: str
    position: int
    content: Optional[str] = None
    revision: int

class OperationCreate(OperationBase):
    user_id: int

class Operation(OperationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
