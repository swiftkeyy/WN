from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PromptTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    title: str
    category: str
    prompt_text: str
    is_active: bool
    created_at: datetime
