from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="documents")
    operations = relationship("Operation", back_populates="document")
    snapshots = relationship("Snapshot", back_populates="document")

class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    op_type = Column(String) # 'insert' or 'delete'
    position = Column(Integer)
    content = Column(String, nullable=True)
    revision = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="operations")

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, ForeignKey("documents.id"))
    content = Column(Text)
    revision = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    document = relationship("Document", back_populates="snapshots")
