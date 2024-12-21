from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db, User, Task

router = APIRouter()

class TaskBase(BaseModel):
    description: str
    location: str = ''
    priority: int = 0
    date_due: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    status: str = ''
    categories: List[str] = []

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int

    class ConfigDict:
        from_attributes = True


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(skip: int = 0, limit: int = 100, include_completed: bool = False, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    if not include_completed:
        query = query.filter(Task.date_completed == None)
    tasks = query.order_by(Task.date_added).offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = Task(**task.model_dump(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.model_dump().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}
