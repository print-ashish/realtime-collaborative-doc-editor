from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

# Create a router instance. 
# prefix="/users" means all routes in this file start with /users
# tags=["users"] helps group these in the Swagger docs (/docs)
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    - user: The data sent by the client (validated by schemas.UserCreate)
    - db: The database session provided by FastAPI's dependency injection
    """
    
    # 1. Check if a user with this email already exists
    # We use .query(models.User) to target the users table
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    # 2. Create the user object using our SQLAlchemy model
    # We "hash" the password manually for now as per our plan
    hashed_password = user.password + "_hashed"
    
    new_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    
    # 3. Save to database
    db.add(new_user)       # Tell SQLAlchemy we want to add this object
    db.commit()            # Save the changes to the database
    db.refresh(new_user)   # Refresh the object to get the generated 'id' from the DB
    
    # 4. Return the user (FastAPI will automatically convert it to schemas.User)
    return new_user
