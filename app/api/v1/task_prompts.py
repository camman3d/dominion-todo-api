from datetime import datetime
from pydantic import BaseModel


class TaskPromptResponse(BaseModel):
    id: int
    ai_prompt_id: int
    result: str
    date_added: datetime

    class ConfigDict:
        from_attributes = True