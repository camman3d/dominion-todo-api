from datetime import datetime
from fastapi import APIRouter
from typing import List, Optional
from fastapi.params import Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.database import User
from functools import reduce

router = APIRouter()

class CreditResponse(BaseModel):
    id: int
    amount: int
    date: datetime
    stripe_payment_id: Optional[str]
    task_prompt_id: Optional[int]

    class ConfigDict:
        from_attributes = True

class CreditBalanceResponse(BaseModel):
    credit_balance: int


@router.get("/", response_model=List[CreditResponse])
async def read_credits(current_user: User = Depends(get_current_user)):
    return current_user.credit_transactions

@router.get("/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(current_user: User = Depends(get_current_user)):
    transactions = current_user.credit_transactions
    credit_total = reduce(lambda a,b: a + b.amount, transactions, 0)
    return {
        "credit_balance": credit_total
    }
