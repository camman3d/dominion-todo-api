from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean

from app.database import Base

router = APIRouter()



class User(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool

    class Config:
        orm_mode = True



@router.get("/", response_model=List[User])
async def read_users():
    # Your user fetching logic here
    return [
        User(id=1, email="user@example.com", name="John Doe")
    ]

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int):
    # Your user fetching logic here
    return User(id=user_id, email="user@example.com", name="John Doe")

@router.post("/", response_model=User)
async def create_user(user: User):
    # Your user creation logic here
    return user