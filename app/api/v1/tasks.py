from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.api.v1.task_prompts import TaskPromptResponse
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

SORT_KEYS = ['date_due', 'date_added', 'date_completed', 'priority']
SORT = {
    'priority': case((Task.priority == 0, 7), else_=Task.priority)
}


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(sort: str = '', filter_name: str = '', skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    if sort in SORT_KEYS:
        if sort in SORT:
            query = query.order_by(SORT[sort])
        else:
            query = query.order_by(getattr(Task, sort))
    query = apply_filter(query, filter_name)

    tasks = query.offset(skip).limit(limit).all()
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

@router.get("/{task_id}/prompts", response_model=List[TaskPromptResponse])
async def read_task_prompts(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.prompts

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


def apply_filter(query, filter_name):
    if filter_name == 'today':
        now = datetime.now(timezone.utc)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

        query = query.filter(Task.date_due != None)
        query = query.filter(Task.date_due <= end_of_day)

    elif filter_name == 'week':
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_day + timedelta(days=7)

        query = query.filter(Task.date_due != None)
        query = query.filter(Task.date_due <= end_of_week)

    elif filter_name == 'high_priority':
        query = query.filter(Task.priority > 0).filter(Task.priority <= 3)

    elif filter_name.startswith('category:'):
        category = filter_name[9:]
        query = query.filter(Task.categories.any(category))

    elif filter_name.startswith('location:'):
        location = filter_name[9:]
        query = query.filter(Task.location == location)

    elif filter_name == 'completed':
        query = query.filter(Task.date_completed != None)

    if filter_name != 'completed':
        query = query.filter(Task.date_completed == None)

    return query