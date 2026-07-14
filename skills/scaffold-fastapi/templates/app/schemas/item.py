from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
