from fastapi import APIRouter, HTTPException
from typing import List
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth import get_password_hash, get_current_admin, generate_salt
from app.database import get_db, User

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool

    class ConfigDict:
        from_attributes = True



@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    salt = generate_salt()
    hashed_password = get_password_hash(user.password, salt)
    db_user = User(email=user.email, hashed_password=hashed_password, salt=salt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user