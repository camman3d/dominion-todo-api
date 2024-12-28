from fastapi import APIRouter, HTTPException
from typing import List, Optional
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.v1.task_prompts import TaskPromptResponse
from app.auth import get_current_user
from app.database import get_db, User, Task, AIPrompt, TaskPrompt, CreditTransaction
from functools import reduce

from app.lib import llm

router = APIRouter()

class PromptResponse(BaseModel):
    id: int
    name: str
    description: str
    cost: int
    returns_json: bool

    class ConfigDict:
        from_attributes = True

class ApplyPromptResponse(BaseModel):
    success: bool
    message: Optional[str]
    task_prompt: Optional[TaskPromptResponse]
    credit_balance: Optional[int]



@router.get("/", response_model=List[PromptResponse])
async def read_prompts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prompts = db.query(AIPrompt).all()
    return prompts

@router.post("/{prompt_id}/apply/{task_id}", response_model=ApplyPromptResponse)
async def apply_prompt_to_task(prompt_id: int, task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Will invoke AI, using the specified prompt template and task to generate the prompt.
    Requires the user to have enough credits to run the prompt. The process is:
    - Check credit balance
    - Generate prompt
    - Invoke AI
    - Save response
    - Deduct credit

    Returns one of:
    ```
    {
        "success": false,
        "message": "...reason",
        "credit_balance": balance
    }
    or
    {
        "success": true,
        "task_prompt": {...resulting TaskPrompt},
        "credit_balance": balance
    }
    ```
    """
    prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    transactions = current_user.credit_transactions
    credit_total = reduce(lambda a,b: a + b.amount, transactions, 0)
    if credit_total < prompt.cost:
        return {
            "success": False,
            "message": "Insufficient credits",
            "task_prompt": None,
            "credit_balance": credit_total,
        }

    # 1. Generate the prompt
    formatted_prompt = prompt.prompt_template.replace('{task_description}', task.description)

    # 2. Call the LLM with the prompt
    result = llm.invoke(formatted_prompt)

    # 3. Save the response
    task_prompt = TaskPrompt(task_id=task_id, ai_prompt_id=prompt.id, result=result)
    db.add(task_prompt)
    db.commit()
    db.refresh(task_prompt)

    # 4. Deduct credit
    transaction = CreditTransaction(user_id=current_user.id, amount=-prompt.cost, task_prompt_id=task_prompt.id)
    db.add(transaction)
    db.commit()

    return {
        "success": True,
        "message": None,
        "task_prompt": task_prompt,
        "credit_balance": credit_total - prompt.cost,
    }
