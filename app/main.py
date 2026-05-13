from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import documents  
from .routers import  users
from .routers import operations

# Create database tables (Initial simplified approach, will use Alembic later)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Collaborative Doc Editor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Real-Time Collaborative Doc Editor API"}

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(operations.router)
# app.include_router(documents.router)
