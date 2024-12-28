from fastapi import APIRouter
from app.api.v1 import users, tasks, prompts, credits

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(credits.router, prefix="/credits", tags=["credits"])
