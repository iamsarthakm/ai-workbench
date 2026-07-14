from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class GenericAPIResponseDetail(BaseModel):
    message: str = Field(default="")
    error_code: str = Field(default="")
    request_id: Optional[str] = None


class GenericApiResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True)
    details: Optional[GenericAPIResponseDetail] = None
    data: Optional[T] = None
