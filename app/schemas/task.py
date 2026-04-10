from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_type: str
    input_text: str | None = None
    input_file_path: str | None = None
    output_file_path: str | None = None
    status: str
    provider: str | None = None
    error_message: str | None = None
    created_at: datetime
